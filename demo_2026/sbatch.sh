#!/bin/bash 
#SBATCH    --job-name=caly
#SBATCH    --ntasks=1
#SBATCH    --ntasks-per-node=1
#SBATCH    --nodes=1
#SBATCH -A groupfromyuxin
#SBATCH --partition=workshop
#SBATCH --output=job.%j.out
#SBATCH --error=job.%j.err

source /public/env/compiler_gcc_14.2.0
source /public/home/mzq001/software/miniforge3/bin/activate /public/home/mzq001/software/miniforge3/envs/calypso-2610
calypso.x