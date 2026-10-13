#!/bin/bash

remote_work_dir=/public/home/mzq001/temp_xinyu_2025/demo/layer_single_layer_H2O/run0/results/opt_task/42
cd ${remote_work_dir}
export -p > ${remote_work_dir}/env
if [ ! -f calypso-42_tag ]; then
echo 'bash run_flow.sh "$CALYPSO_MLP_CMD"' > temp_script.sh
timeout -k 10 3600s  bash temp_script.sh  > calypso-42.log 2>&1 && touch calypso-42_tag
exit_code=$?
if [ "$exit_code" == 124 ]; then
    touch timeout_tag
    exit_code=0
elif [ "$exit_code" != 0 ]; then
    echo "Command failed with exit code $exit_code"
fi
fi
