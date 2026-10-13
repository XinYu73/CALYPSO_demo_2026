#!/bin/bash

# sub_calypso-43.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/layer_double_layer_CrI3/reference/results/opt_task/43/calypso-43.sh > /public/home/mzq001/temp_xinyu_2025/demo/layer_double_layer_CrI3/reference/results/opt_task/43/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!