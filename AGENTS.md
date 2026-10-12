use conda env "calypso_dev"

fetch newest code 

git -c fetch.recurseSubmodules=false pull origin main
git submodule sync --recursive
git submodule update --init --recursive
