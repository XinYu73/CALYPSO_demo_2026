
#!/usr/bin/env bash

command=$1
$command calypso_run_mlp.py > opt.log 2>&1 >> opt.log 2>&1
