#!/bin/bash

# sub_calypso-3.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/cluster_normal_CH4/reference/results/opt_task/3/calypso-3.sh > /public/home/mzq001/temp_xinyu_2025/demo/cluster_normal_CH4/reference/results/opt_task/3/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!