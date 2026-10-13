#!/bin/bash

# sub_calypso-3.sh

{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/bulk_substitute_LaFeO3/run/results/opt_task/3/calypso-3.sh > /public/home/mzq001/temp_xinyu_2025/demo/bulk_substitute_LaFeO3/run/results/opt_task/3/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!