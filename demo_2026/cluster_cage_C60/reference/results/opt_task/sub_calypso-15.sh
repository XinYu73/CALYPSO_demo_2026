#!/bin/bash

# sub_calypso-15.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/cluster_cage_C60/reference/results/opt_task/15/calypso-15.sh > /public/home/mzq001/temp_xinyu_2025/demo/cluster_cage_C60/reference/results/opt_task/15/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!