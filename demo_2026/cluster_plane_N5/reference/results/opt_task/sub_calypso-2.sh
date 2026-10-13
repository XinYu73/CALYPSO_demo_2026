#!/bin/bash

# sub_calypso-2.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/cluster_plane_N5/reference/results/opt_task/2/calypso-2.sh > /public/home/mzq001/temp_xinyu_2025/demo/cluster_plane_N5/reference/results/opt_task/2/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!