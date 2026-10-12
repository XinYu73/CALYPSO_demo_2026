#!/bin/bash 
#SBATCH    --job-name=caly
#SBATCH    --ntasks=1
#SBATCH    --ntasks-per-node=1
##SBATCH    --time=3:00:00
#SBATCH    --nodes=1
#SBATCH -A groupfromyuxin
#SBATCH --partition=workshop
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err


# source /public/home/mzq001/software/miniconda3/bin/activate /public/home/mzq001/software/miniconda3/envs/calypso

# conda activate calypso
calypso.x

