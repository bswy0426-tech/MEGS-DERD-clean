#!/usr/bin/env bash
set -euo pipefail

CONFIG="${1:-configs/TUM_VIE/mocap-desk.yaml}"

: "${DERDNET_MODEL_PATH:?Please export DERDNET_MODEL_PATH first.}"
: "${TUM_VIE_ROOT:?Please export TUM_VIE_ROOT first.}"

python main.py --config "$CONFIG"
