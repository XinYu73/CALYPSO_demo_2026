#!/bin/bash

# sub_calypso-192.sh

{ nohup bash -c 'bash /public/home/mzq001/temp_xinyu_2025/demo/bulk_substitute_LaFeO3/run/results/opt_task/192/calypso-192.sh > /public/home/mzq001/temp_xinyu_2025/demo/bulk_substitute_LaFeO3/run/results/opt_task/192/submit.log 2>&1; '> /dev/null 2>&1 &} && echo $!