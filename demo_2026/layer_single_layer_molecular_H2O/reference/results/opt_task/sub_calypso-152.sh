#!/bin/bash

# sub_calypso-152.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/layer_single_layer_H2O/run0/results/opt_task/152/calypso-152.sh > /public/home/mzq001/temp_xinyu_2025/demo/layer_single_layer_H2O/run0/results/opt_task/152/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!