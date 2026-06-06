#!/usr/bin/env bash
set -u

echo "===== Python ====="
which python
python --version

echo "===== Imports ====="
python - <<'PY'
import importlib

modules = [
    "numpy",
    "torch",
    "pypose",
    "imageio",
    "cv2",
    "yaml",
    "tqdm",
    "scipy",
    "skimage",
    "lpips",
    "h5py",
    "hdf5plugin",
]

for name in modules:
    mod = importlib.import_module(name)
    version = getattr(mod, "__version__", "ok")
    print(f"{name}: {version}")

import numpy as np
import torch

print("cuda available:", torch.cuda.is_available())
print("torch cuda:", torch.version.cuda)
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))

major = int(np.__version__.split(".")[0])
if major >= 2:
    raise SystemExit("NumPy must be < 2 for this runtime.")
PY

echo "===== Environment Variables ====="
echo "DERDNET_MODEL_PATH=${DERDNET_MODEL_PATH:-}"
echo "TUM_VIE_ROOT=${TUM_VIE_ROOT:-}"
echo "REPLICA_EVENT_ROOT=${REPLICA_EVENT_ROOT:-}"

echo "===== File Checks ====="
if [ -n "${DERDNET_MODEL_PATH:-}" ]; then
  ls -lh "$DERDNET_MODEL_PATH"
fi

if [ -n "${TUM_VIE_ROOT:-}" ]; then
  ls -lh "$TUM_VIE_ROOT" | head
fi

echo "Environment check finished."
