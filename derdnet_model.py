# derdnet_model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class PixelwiseConvGRU(nn.Module):
    """
    A neural network class to predict pixel-wise depth.
    Input: Sub-DSI
    Output: Depth estimate for central pixel and, if multi-pixel is set to True, also of the 8 dircetly neighboring pixels
    Architecture: 3D-Convolution -> Flatten -> GRU -> Final hidden state -> Dense layer -> Output.
    
    Args:
        sub_frame_radius_h (int): Radius at the length axis of the frame of the Sub-DSI.
        sub_frame_radius_w (int): Radius at the length axis of the frame of the Sub-DSI.
        out_channels (int): Number of output channels for the 3D-convolution.
        multi_pixel (bool): Decides whether depth shall be estimated only for the central pixel or also at the 8 neighboring pixels.
        use_pixel_pos (bool): An option to append the pixel coordinates to the data vector after the GRU for additional information.
                                Pixel positions must be normalized herefor by the DSI_Pixelswise_Dataset.
        hidden_size_scale (int): A scaling factor to scale the size of the inputs for the GRU to the size of the hidden states.
        num_gru_layers (int): Defines how many GRU layers should be stacked sequentially.
        bidirectional (bool): Defines whether the GRU layer(s) should work bidirectionally.
        dropout_rate (float): Rate for dropout.
    """
    
    def __init__(self,
                 sub_frame_radius_h,
                 sub_frame_radius_w,
                 out_channels=4,
                 multi_pixel=False,
                 use_pixel_pos=False,
                 hidden_size_scale=1,
                 num_gru_layers=1,
                 bidirectional=False,
                 dropout_rate=0
                ):
        # Inherit
        super(PixelwiseConvGRU, self).__init__()
    
        # Args
        self.sub_frame_radius_h = sub_frame_radius_h
        self.sub_frame_radius_w = sub_frame_radius_w        
        # The size of the Sub-DSI frame is 2 times its radius plus the central pixel
        self.sub_frame_size_h = 2 * sub_frame_radius_h + 1
        self.sub_frame_size_w = 2 * sub_frame_radius_w + 1
        self.out_channels = out_channels
        self.multi_pixel = multi_pixel
        self.use_pixel_pos = use_pixel_pos
        self.hidden_size_scale = hidden_size_scale
        self.num_gru_layers = num_gru_layers
        self.bidirectional = bidirectional
        self.dropout_rate = dropout_rate

        # Deduct sizes
        self.gru_input_size = self.out_channels * (self.sub_frame_size_h-2) * (self.sub_frame_size_w-2)  # Frame size is reduced since we do not apply padding
        self.gru_hidden_size = self.gru_input_size * self.hidden_size_scale
        self.output_dim = 1 if not self.multi_pixel else 9
        
        # 3D-convolution layer
        self.conv3d = nn.Sequential(
            nn.Conv3d(
                in_channels=1,
                out_channels=self.out_channels,
                kernel_size=(3, 3, 3),
                # Pad only along the depth dimension
                # since ray counts are effectively zero for the padded depth levels
                padding=(1, 0, 0), 
                stride=(2,1,1)
            ),
            nn.ReLU(),
            nn.Dropout(self.dropout_rate)
            )
        
        # GRU layer
        self.gru = nn.GRU(
            input_size = self.gru_input_size,
            hidden_size = self.gru_hidden_size,
            num_layers = self.num_gru_layers,
            dropout = self.dropout_rate,
            bidirectional=self.bidirectional,
            batch_first = True
            )

        # Output layer
        self.dense_output = nn.Sequential(
            nn.Linear(
                # A bidircetional GRU would have double the output size
                # and if the pixel position shall be considered, two entries will be appended
                (1+self.bidirectional)*self.gru_hidden_size + 2*self.use_pixel_pos, self.gru_hidden_size),
            nn.ReLU(),
            nn.Dropout(self.dropout_rate),
            nn.Linear(self.gru_hidden_size, self.output_dim)
            )

        # Automatically send model to the available device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)  # Send the model to the device
        
    def forward(self, input):
        # Preprocess input
        pixel_position, sub_dsi = input
        batch_size, depth_levels = sub_dsi.shape[:2]
        
        # Apply 3D-convolution
        sub_dsi_conv = self.conv3d(sub_dsi.unsqueeze(dim=1))
        # Flatten
        sub_dsi_conv_flat = sub_dsi_conv.transpose(1,2).flatten(start_dim=2)
        # Check whether dimensions match from 3D-convolution to GRU
        batch_size, depth_levels, tensor_size = sub_dsi_conv_flat.size()
        assert tensor_size == self.gru_input_size
        
        # Apply GRU
        h_seq, _ = self.gru(sub_dsi_conv_flat)
        # Take final hidden state
        h_n = h_seq[:,-1,:]
        # If selected, appenid pixel position
        if self.use_pixel_pos:
            h_n = torch.cat([pixel_position, h_n], dim=-1)
        # Check whether dimensions match from GRU output to the final dense output-layer
        assert h_n.size() == (batch_size, (1+self.bidirectional)*self.gru_hidden_size + 2*self.use_pixel_pos)

        # Apply final dense layer to obtain final estimate
        output = self.dense_output(h_n)
        # Assert correct output dimension
        assert output.size() == (batch_size, self.output_dim)
        # Squeeze if single pixel
        if not self.multi_pixel:
            output = output.squeeze(dim=-1)
        
        return output

    def save_model(self, optimizer, model_file, model_path=None, print_save=True):
        """Method to save model and optimizer parameters to model_path and model_file."""
        if model_path is None:
            # Set default model path
            model_path = f"./models/"
            
        torch.save({
            "model_state_dict": self.state_dict(),
            "optimizer_state_dict": optimizer.state_dict()},
            os.path.join(model_path, model_file)
                  )
        # Print success message
        if print_save:
            print(f"Saved PyTorch Model and Optimizer State to {model_path}{model_file}")

    def load_parameters(self, model_file, model_path=None, optimizer=None):
        """Method to load model parameters from model_path and model_file.
        If an optimizer is selected, its parameters are loaded, too.
        """
        if model_path is None:
            # Set default model path
            model_path = f"./models/"
        checkpoint = torch.load(os.path.join(model_path, model_file), map_location=self.device)
        self.load_state_dict(checkpoint["model_state_dict"])
        if optimizer is not None:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])