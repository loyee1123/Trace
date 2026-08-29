#!/bin/bash
#SBATCH --job-name=qwen38-vllm
#SBATCH --partition=ica100
#SBATCH --gres=gpu:a100:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=02:00:00
#SBATCH --output=/scratch4/kding1/Trace/qwen/logs/vllm-%j.log

export HF_HOME=/scratch4/kding1/huggingface/hf-home
# 节点默认 module 的老 libstdc++ 缺 CXXABI_1.3.15, 让 conda env 的排最前
module purge 2>/dev/null || true
export LD_LIBRARY_PATH=/scratch4/kding1/envs/trace/lib:$LD_LIBRARY_PATH
# Triton JIT 需要 CUDA 工具链(cuda.h / ptxas), 都在 conda env 里
export PATH=/scratch4/kding1/envs/trace/bin:$PATH
export TRITON_PTXAS_PATH=/scratch4/kding1/envs/trace/bin/ptxas
export CUDA_HOME=/scratch4/kding1/envs/trace

echo "== vLLM serving Qwen3.8-27B on node: $(hostname) port 8000 =="

/scratch4/kding1/envs/trace/bin/vllm serve Qwen/Qwen3.8-27B \
    --served-model-name qwen3.8-27b \
    --tensor-parallel-size 2 \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 32768 \
    --max-num-batched-tokens 20480 \
    --reasoning-parser qwen3 \
    --gpu-memory-utilization 0.90
