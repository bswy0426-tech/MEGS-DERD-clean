# MEGS DERD-Net Clean Release

This repository contains the cleaned MEGS code used for monocular event-based
3D Gaussian Splatting with DERD-Net depth supervision. The repository keeps the
DERD-Net depth-prior path and removes unused or deprecated depth branches.

## What Is Included

- Event-only monocular 3DGS tracking and mapping.
- DSI-based DERD-Net depth initialization and online depth consistency.
- Environment-variable based dataset/model paths for reproducible runs.

## Path Setup

Set these paths before running experiments.

PowerShell:

```powershell
$env:DERDNET_MODEL_PATH="<path-to>\derdnet_indoor_depth_model.pth"
$env:TUM_VIE_ROOT="<path-to>\TUM-VIE"
$env:REPLICA_EVENT_ROOT="<path-to>\ReplicaEvent"
```

Bash:

```bash
export DERDNET_MODEL_PATH=/path/to/derdnet_indoor_depth_model.pth
export TUM_VIE_ROOT=/path/to/TUM-VIE
export REPLICA_EVENT_ROOT=/path/to/ReplicaEvent
```

The checkpoint filename does not need to match the original DERD-Net release
name. Keep large checkpoints and datasets outside git.

## Example Runs

TUM-VIE:

```bash
python main.py --config configs/TUM_VIE/mocap-6dof.yaml
```

Replica:

```bash
python main.py --config configs/SimuEvent/replica_office3.yaml
```

## Environment Pack

Server setup files are included for reproducibility:

- `FEATURIZE_SETUP.md`: Featurize setup and run instructions.
- `constraints-featurize.txt`: pinned dependency versions that keep NumPy below 2.
- `requirements-featurize.txt`: Featurize dependency checklist.
- `environment.yml`: optional conda environment template.
- `configs/runtime/featurize_env.example`: environment variable template.
- `scripts/install_featurize_deps.sh`: repair/install Python dependencies without upgrading NumPy to 2.x.
- `scripts/check_featurize_env.sh`: runtime/import/path checker.
- `scripts/setup_featurize_cuda.sh`: sourceable CUDA/gsplat include and linker setup.
- `scripts/run_tumvie.sh`: TUM-VIE launch helper.

On Featurize, the stable setup sequence is:

```bash
cd /home/featurize/work/MEGS-DERD-clean
source /home/featurize/work/envs/megs-derd/bin/activate
bash scripts/install_featurize_deps.sh
source configs/runtime/featurize_env.example
source scripts/setup_featurize_cuda.sh
```

Then verify the local CUDA backend:

```bash
python - <<'PY'
from gsplat.cuda._backend import _C
print("gsplat backend:", _C)
PY
```

## DERD-Net Depth Error Experiment

`DEPTH_ERROR_EXPERIMENT.md` describes the sensitivity experiment for the paper.
The depth perturbation hook is built into `main.py` and is disabled by default,
so the verified DERD-Net path is unchanged unless `depth_error_exp.enable` is
set to `true` in the YAML config.

Example office3 depth-error runs:

```bash
export DERDNET_MODEL_PATH=/home/featurize/work/checkpoints/derdnet_indoor_depth_prior.pth
export REPLICA_EVENT_ROOT=/home/featurize/work/IncEventGS/data/event_replica

python main.py --config configs/DepthError/replica_office3_clean.yaml
python main.py --config configs/DepthError/replica_office3_noise005.yaml
python main.py --config configs/DepthError/replica_office3_noise010.yaml
python main.py --config configs/DepthError/replica_office3_noise020.yaml
python main.py --config configs/DepthError/replica_office3_noise050.yaml
```

## Notes

- The code path is DERD-Net based.
- Depth perturbation experiments are opt-in and leave normal runs unchanged.
- Outputs, datasets, and pretrained weights are ignored by git.
- The config loader expands environment variables in YAML files.
