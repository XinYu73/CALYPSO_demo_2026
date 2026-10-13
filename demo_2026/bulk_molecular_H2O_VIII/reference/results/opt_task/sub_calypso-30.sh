#!/bin/bash

# sub_calypso-30.sh

{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/bulk_molecular_H2O_VIII/results/opt_task/30/calypso-30.sh > /public/home/mzq001/temp_xinyu_2025/demo/bulk_molecular_H2O_VIII/results/opt_task/30/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!