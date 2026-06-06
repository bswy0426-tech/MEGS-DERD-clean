# Featurize Setup Pack

This file records the server-side environment and run configuration for MEGS-DERD.

## 1. Clone

```bash
cd /home/featurize/work
git clone https://github.com/bswy0426-tech/MEGS-DERD-clean.git
cd MEGS-DERD-clean
```

If the repository is private, use a GitHub token or temporarily make the
repository public before cloning.

## 2. Install Runtime Overlay

Use the existing Featurize Python/PyTorch runtime when possible, then install
only the missing Python packages.

```bash
python -m pip install --user --force-reinstall "numpy==1.26.4"
python -m pip install --user -r requirements-featurize.txt
python -m pip install --user --no-deps pypose
```

The NumPy pin is important. Some CUDA/PyTorch modules on the server may be
compiled against NumPy 1.x and can fail with NumPy 2.x.
Install `pypose` with `--no-deps` on Featurize so pip does not replace the
preinstalled PyTorch/CUDA stack.

## 3. Prepare Checkpoint and Data Paths

Keep large checkpoints outside git. Put the DERD-Net checkpoint under a neutral
local name:

```bash
mkdir -p /home/featurize/work/checkpoints
cp /path/to/source_derdnet_checkpoint.pth \
   /home/featurize/work/checkpoints/derdnet_indoor_depth_prior.pth
```

Set environment variables:

```bash
export DERDNET_MODEL_PATH=/home/featurize/work/checkpoints/derdnet_indoor_depth_prior.pth
export TUM_VIE_ROOT=/home/featurize/work/MEGS-main/data/tum_vie
```

For Replica experiments, also set:

```bash
export REPLICA_EVENT_ROOT=/home/featurize/work/MEGS-main/data
```

The same exports are stored in:

```bash
configs/runtime/featurize_env.example
```

You can load them with:

```bash
source configs/runtime/featurize_env.example
```

## 4. Verify Environment

```bash
bash scripts/check_featurize_env.sh
```

Expected checks:

- NumPy version is 1.26.x.
- PyTorch imports successfully.
- CUDA is available.
- `pypose`, `imageio`, `cv2`, `yaml`, `tqdm`, `scipy`, `skimage`,
  `h5py`, and `hdf5plugin` import successfully.
- `DERDNET_MODEL_PATH` points to an existing `.pth` file.
- `TUM_VIE_ROOT` points to the TUM-VIE dataset root.

## 5. Run TUM-VIE

Start with the sequence that is already extracted:

```bash
bash scripts/run_tumvie.sh configs/TUM_VIE/mocap-desk.yaml
```

Other TUM-VIE configs:

```bash
bash scripts/run_tumvie.sh configs/TUM_VIE/mocap-1d-trans.yaml
bash scripts/run_tumvie.sh configs/TUM_VIE/mocap-3d-trans.yaml
bash scripts/run_tumvie.sh configs/TUM_VIE/mocap-6dof.yaml
bash scripts/run_tumvie.sh configs/TUM_VIE/mocap-desk2.yaml
```

If a sequence only exists as a zip file, extract it before running the
corresponding config.

## 6. Depth Error Experiment

Edit the target config and enable:

```yaml
depth_error_exp:
  enable: true
  mode: gaussian_rel
  sigma: 0.1
```

See `DEPTH_ERROR_EXPERIMENT.md` for the recommended table and experiment modes.
