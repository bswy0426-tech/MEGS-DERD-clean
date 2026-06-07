#!/usr/bin/env bash
set -euo pipefail

# Featurize image path used by the verified MEGS-DERD runtime.
# Source this file before the first gsplat CUDA backend build:
#   source scripts/setup_featurize_cuda.sh
#
# Running it with `bash scripts/setup_featurize_cuda.sh` can verify the paths,
# but the exports will not remain in the parent shell. For experiments, source
# the script or source configs/runtime/featurize_env.example.

export PYTHONNOUSERSITE=1

export CUDA_HOME=${CUDA_HOME:-/environment/miniconda3}
export CUDA_RUNTIME_H=${CUDA_RUNTIME_H:-$(find /environment/miniconda3 /home/featurize/work/envs/megs-derd -type f -name cuda_runtime.h 2>/dev/null | head -1)}
export THRUST_COMPLEX_H=${THRUST_COMPLEX_H:-$(find /environment/miniconda3 /home/featurize/work/envs/megs-derd -type f -path "*/thrust/complex.h" 2>/dev/null | head -1)}
export CUDART_SO=${CUDART_SO:-$(find /environment/miniconda3 /home/featurize/work/envs/megs-derd -type f -name "libcudart.so*" 2>/dev/null | head -1)}

if [ -z "${CUDA_RUNTIME_H:-}" ]; then
  echo "ERROR: cuda_runtime.h was not found. Install CUDA runtime headers first." >&2
  return 1 2>/dev/null || exit 1
fi

if [ -z "${THRUST_COMPLEX_H:-}" ]; then
  echo "ERROR: thrust/complex.h was not found. Install cuda-cccl first." >&2
  return 1 2>/dev/null || exit 1
fi

if [ -z "${CUDART_SO:-}" ]; then
  echo "ERROR: libcudart.so.* was not found. Install CUDA runtime first." >&2
  return 1 2>/dev/null || exit 1
fi

export CUDA_RUNTIME_INC=$(dirname "$CUDA_RUNTIME_H")
export CUDA_CCCL_INC=$(dirname "$(dirname "$THRUST_COMPLEX_H")")

mkdir -p /home/featurize/work/cuda_lib_links
ln -sf "$CUDART_SO" /home/featurize/work/cuda_lib_links/libcudart.so
export CUDA_LIB=/home/featurize/work/cuda_lib_links

export PATH="$CUDA_HOME/bin:$PATH"
export CPATH="$CUDA_RUNTIME_INC:$CUDA_CCCL_INC:${CPATH:-}"
export C_INCLUDE_PATH="$CUDA_RUNTIME_INC:$CUDA_CCCL_INC:${C_INCLUDE_PATH:-}"
export CPLUS_INCLUDE_PATH="$CUDA_RUNTIME_INC:$CUDA_CCCL_INC:${CPLUS_INCLUDE_PATH:-}"
export LIBRARY_PATH="$CUDA_LIB:${LIBRARY_PATH:-}"
export LD_LIBRARY_PATH="$CUDA_LIB:$(dirname "$CUDART_SO"):${LD_LIBRARY_PATH:-}"
export MAX_JOBS=${MAX_JOBS:-4}

echo "CUDA_HOME=$CUDA_HOME"
echo "CUDA_RUNTIME_INC=$CUDA_RUNTIME_INC"
echo "CUDA_CCCL_INC=$CUDA_CCCL_INC"
echo "CUDA_LIB=$CUDA_LIB"
echo "CUDART_SO=$CUDART_SO"
echo "MAX_JOBS=$MAX_JOBS"
which nvcc || true
nvcc --version || true
