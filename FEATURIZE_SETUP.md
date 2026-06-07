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

## 2. Check Runtime Dependencies

Use the existing Featurize Python/PyTorch runtime when possible. Do not blindly
run a full requirements installation on a working image, because pip may replace
the preinstalled PyTorch/CUDA stack.

```bash
python -c "import numpy, torch; print('numpy', numpy.__version__); print('torch', torch.__version__, torch.cuda.is_available())"
bash scripts/check_featurize_env.sh
```

If a package is missing, install only that package. Examples:

```bash
python -m pip install --user h5py hdf5plugin
python -m pip install --user numba
python -m pip install --user trimesh
```

If `pypose` is missing, install it without dependencies so pip does not replace
torch:

```bash
python -m pip install --user --no-deps pypose
```

If NumPy was accidentally upgraded to 2.x and PyTorch starts warning about
compiled modules, downgrade NumPy only:

```bash
python -m pip install --user --force-reinstall "numpy==1.26.4"
```

`requirements-featurize.txt` is a reference checklist, not the default install
command.

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
export REPLICA_EVENT_ROOT=/home/featurize/data/event_replica
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

- NumPy version is 1.26.x or another NumPy 1.x release.
- PyTorch imports successfully.
- CUDA is available.
- `pypose`, `imageio`, `cv2`, `yaml`, `tqdm`, `scipy`, `skimage`,
  `h5py`, `hdf5plugin`, `trimesh`, `sklearn`, `kornia`, `jaxtyping`,
  `pytorch_msssim`, `plyfile`, `numba`, and `torchgeometry` import
  successfully.
- `DERDNET_MODEL_PATH` points to an existing `.pth` file.
- `TUM_VIE_ROOT` points to the TUM-VIE dataset root.

## 5. Prepare gsplat CUDA Backend

The server must compile the local `gsplat` CUDA extension before training. If
`gsplat: No CUDA toolkit found` appears, source the helper script:

```bash
source scripts/setup_featurize_cuda.sh
```

Then verify:

```bash
python - <<'PY'
from gsplat.cuda._backend import _C
print("gsplat backend:", _C)
PY
```

Expected output should point to a compiled `gsplat_cuda.so` file, not `None`.

## 6. Run TUM-VIE

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

## 7. Depth Error Experiment

See `DEPTH_ERROR_EXPERIMENT.md` for the recommended table and perturbation
protocol. The clean runtime keeps the verified DERD-Net behavior unchanged, so
add an explicit perturbation hook before treating those settings as executable
config options.
