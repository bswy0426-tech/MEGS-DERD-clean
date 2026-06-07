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

## 2. Repair Runtime Dependencies

Use the existing Featurize Python/PyTorch runtime when possible. Do not blindly
run a full requirements installation on a working image, because pip may replace
the preinstalled PyTorch/CUDA stack.

The verified repair command is:

```bash
source /home/featurize/work/envs/megs-derd/bin/activate
bash scripts/install_featurize_deps.sh
```

This script pins NumPy to `1.26.4`. Do not install unconstrained latest
`opencv-python-headless`, `plyfile`, `scipy`, or `numba`, because pip may pull
NumPy 2.x and break PyTorch with `RuntimeError: Numpy is not available`.

After repair, check the runtime:

```bash
python -c "import numpy, torch; print('numpy', numpy.__version__); print('torch', torch.__version__, torch.cuda.is_available())"
bash scripts/check_featurize_env.sh
```

If NumPy was accidentally upgraded to 2.x, run the repair script again instead
of installing packages one by one:

```bash
bash scripts/install_featurize_deps.sh
```

`constraints-featurize.txt` stores the pinned versions. `requirements-featurize.txt`
is a checklist and should be used with `-c constraints-featurize.txt` if needed.

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
export REPLICA_EVENT_ROOT=/home/featurize/work/IncEventGS/data/event_replica
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
`gsplat: No CUDA toolkit found`, `cuda_runtime.h` missing, `thrust/complex.h`
missing, or `cannot find -lcudart` appears, source the helper script:

```bash
source configs/runtime/featurize_env.example
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
After this succeeds once, the compiled backend is cached under
`~/.cache/torch_extensions/py311_cu121/gsplat_cuda/`.

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
the perturbation settings are opt-in through `configs/DepthError/*.yaml`.
