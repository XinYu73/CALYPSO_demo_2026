#!/bin/bash

# sub_calypso-59.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/layer_single_layer_H2O/run0/results/opt_task/59/calypso-59.sh > /public/home/mzq001/temp_xinyu_2025/demo/layer_single_layer_H2O/run0/results/opt_task/59/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!