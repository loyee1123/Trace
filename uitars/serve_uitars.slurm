#!/bin/bash
#SBATCH --job-name=uitars-vllm
#SBATCH --partition=a100
#SBATCH --gres=gpu:a100:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=/scratch4/kding1/Trace/uitars/logs/vllm-%j.log

export HF_HOME=/scratch4/kding1/huggingface/hf-home

echo "== vLLM serving UI-TARS-1.5-7B on node: $(hostname) port 8000 =="

/scratch4/kding1/envs/Aria_conda/bin/vllm serve ByteDance-Seed/UI-TARS-1.5-7B \
    --served-model-name ui-tars-1.5-7b \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 32768 \
    --limit-mm-per-prompt '{"image": 10}'
