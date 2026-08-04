#!/bin/bash
#SBATCH --job-name=opencua-vllm
#SBATCH --partition=a100
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/scratch4/kding1/Trace/opencua/logs/vllm-%j.log

export HF_HOME=/scratch4/kding1/huggingface/hf-home
# 节点默认 module 会把老 gcc-9 的 libstdc++ 放进 LD_LIBRARY_PATH，缺 CXXABI_1.3.15；
# 必须让 conda 环境自带的新版排最前
module purge 2>/dev/null || true
export LD_LIBRARY_PATH=/scratch4/kding1/envs/trace/lib:$LD_LIBRARY_PATH
# Triton JIT 需要 CUDA 工具链（ptxas 等），都在 conda env 里
export PATH=/scratch4/kding1/envs/trace/bin:$PATH
export TRITON_PTXAS_PATH=/scratch4/kding1/envs/trace/bin/ptxas
export CUDA_HOME=/scratch4/kding1/envs/trace

echo "== vLLM serving OpenCUA-7B on node: $(hostname) port 8000 =="

/scratch4/kding1/envs/trace/bin/vllm serve xlangai/OpenCUA-7B \
    --served-model-name opencua-7b \
    --trust-remote-code \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 32768 \
    --max-num-batched-tokens 20480
