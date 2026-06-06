# MEGS DERD-Net Clean Release

This repository contains the cleaned MEGS code used for monocular event-based
3D Gaussian Splatting with DERD-Net depth supervision. The repository keeps the
DERD-Net depth-prior path and removes unused or deprecated depth branches.

## What Is Included

- Event-only monocular 3DGS tracking and mapping.
- DSI-based DERD-Net depth initialization and online depth consistency.
- Configurable depth-error experiments for sensitivity analysis.
- Environment-variable based dataset/model paths for reproducible runs.

## Path Setup

Set these paths before running experiments.

PowerShell:

```powershell
$env:DERDNET_MODEL_PATH="D:\path\to\derdnet_indoor_depth_model.pth"
$env:TUM_VIE_ROOT="D:\path\to\TUM-VIE"
$env:REPLICA_EVENT_ROOT="D:\path\to\ReplicaEvent"
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
- `requirements-featurize.txt`: runtime dependency overlay with `numpy==1.26.4`.
- `environment.yml`: optional conda environment template.
- `configs/runtime/featurize_env.example`: environment variable template.
- `scripts/check_featurize_env.sh`: runtime/import/path checker.
- `scripts/run_tumvie.sh`: TUM-VIE launch helper.

## DERD-Net Depth Error Experiment

Depth perturbation is controlled by `depth_error_exp` in the config file.

```yaml
depth_error_exp:
  enable: true
  mode: gaussian_rel
  sigma: 0.1
  scale_factor: 1.0
  dropout_ratio: 0.3
```

Available modes:

- `gaussian_rel`: adds relative Gaussian noise to depth.
- `scale`: multiplies depth by a constant scale factor.
- `dropout`: randomly removes a fraction of valid depth pixels.
- `none`: keeps depth unchanged.

Use this experiment to report how DERD-Net depth errors affect final NVS and
trajectory results.

## Notes

- The code path is DERD-Net based.
- Outputs, datasets, and pretrained weights are ignored by git.
- The config loader expands environment variables in YAML files.
