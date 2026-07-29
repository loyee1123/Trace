#!/bin/bash
#SBATCH --job-name=drvchk
#SBATCH --gres=gpu:1
#SBATCH --time=00:02:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
echo "node: $(hostname)"
nvidia-smi --query-gpu=driver_version --format=csv,noheader | head -1
