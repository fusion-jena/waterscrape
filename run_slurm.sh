#!/bin/bash
#SBATCH --job-name=thwic
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=01:00:00          # Max runtime: 1 hour
#SBATCH --output=thwic.out.%j    # stdout log
#SBATCH --error=thwic.err.%j     # stderr log

# Load CUDA
module load nvidia/cuda/11.7

source /vast/$USER/venv/bin/activate

python3 analysis.py "$1"
