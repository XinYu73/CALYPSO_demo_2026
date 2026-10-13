#!/bin/bash

# sub_calypso-10.sh
export CALYPSO_MLP_CMD='/public/home/lvjian/software/anaconda3/envs/chgnet/bin/python'
{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/layer_double_layer_BaBr3_Graphene/reference/results/opt_task/10/calypso-10.sh > /public/home/mzq001/temp_xinyu_2025/demo/layer_double_layer_BaBr3_Graphene/reference/results/opt_task/10/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!