#!/bin/bash

# sub_calypso-2.sh

{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/bulk_molecular_H2O_VIII/results/opt_task/2/calypso-2.sh > /public/home/mzq001/temp_xinyu_2025/demo/bulk_molecular_H2O_VIII/results/opt_task/2/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!