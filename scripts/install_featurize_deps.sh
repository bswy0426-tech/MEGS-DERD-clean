#!/usr/bin/env bash
set -euo pipefail

# Repair the Featurize Python environment without upgrading the PyTorch/CUDA
# stack or pulling NumPy 2.x. Run this inside the intended virtual environment:
#
#   source /home/featurize/work/envs/megs-derd/bin/activate
#   bash scripts/install_featurize_deps.sh

cd "$(dirname "$0")/.."

export PYTHONNOUSERSITE=1

python -m pip uninstall -y \
  numpy scipy scikit-learn scikit-image opencv-python opencv-python-headless \
  numba plyfile || true

python -m pip install --no-cache-dir --force-reinstall -c constraints-featurize.txt \
  numpy scipy scikit-learn scikit-image numba

python -m pip install --no-cache-dir --no-deps \
  opencv-python-headless==4.8.1.78 plyfile==1.0.3

python -m pip install --no-cache-dir --no-deps pypose

python -m pip install --no-cache-dir -c constraints-featurize.txt \
  imageio imageio-ffmpeg h5py hdf5plugin trimesh jaxtyping \
  torchgeometry kornia pytorch-msssim tqdm pyyaml matplotlib lpips

python - <<'PY'
import importlib
import numpy
import torch

modules = [
    "imageio",
    "pypose",
    "scipy",
    "sklearn",
    "skimage",
    "h5py",
    "hdf5plugin",
    "numba",
    "trimesh",
    "jaxtyping",
    "torchgeometry",
    "kornia",
    "pytorch_msssim",
    "plyfile",
    "tqdm",
    "cv2",
    "yaml",
    "matplotlib",
    "lpips",
]

for name in modules:
    importlib.import_module(name)

print("numpy", numpy.__version__)
print("torch", torch.__version__, torch.cuda.is_available())
print("deps ok")

if int(numpy.__version__.split(".")[0]) >= 2:
    raise SystemExit("NumPy must be < 2.")
PY
