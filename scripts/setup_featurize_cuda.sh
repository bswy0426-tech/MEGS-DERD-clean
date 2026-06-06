#!/usr/bin/env bash
set -euo pipefail

# Featurize image path used by the verified MEGS-DERD runtime.
# Source this file before the first gsplat CUDA backend build:
#   source scripts/setup_featurize_cuda.sh

export PYTHONNOUSERSITE=1

export CUDA_HOME=${CUDA_HOME:-/environment/miniconda3}
export CUDA_TARGET_INC=${CUDA_TARGET_INC:-/environment/miniconda3/targets/x86_64-linux/include}
export CUDA_CCCL_INC=${CUDA_CCCL_INC:-/environment/miniconda3/targets/x86_64-linux/include/cccl}
export CUDA_LIB=${CUDA_LIB:-/environment/miniconda3/lib}

export PATH="$CUDA_HOME/bin:$PATH"
export CPATH="$CUDA_CCCL_INC:$CUDA_TARGET_INC:${CPATH:-}"
export C_INCLUDE_PATH="$CUDA_CCCL_INC:$CUDA_TARGET_INC:${C_INCLUDE_PATH:-}"
export CPLUS_INCLUDE_PATH="$CUDA_CCCL_INC:$CUDA_TARGET_INC:${CPLUS_INCLUDE_PATH:-}"
export LIBRARY_PATH="$CUDA_LIB:${LIBRARY_PATH:-}"
export LD_LIBRARY_PATH="$CUDA_LIB:${LD_LIBRARY_PATH:-}"
export MAX_JOBS=${MAX_JOBS:-4}

echo "CUDA_HOME=$CUDA_HOME"
echo "CUDA_TARGET_INC=$CUDA_TARGET_INC"
echo "CUDA_CCCL_INC=$CUDA_CCCL_INC"
echo "CUDA_LIB=$CUDA_LIB"
echo "MAX_JOBS=$MAX_JOBS"
which nvcc || true
nvcc --version || true

