#!/bin/bash
cd "$(dirname "$0")"
bash ./build/tools/pypi.sh
echo
cd ./src/gdf/_scripts/
bash pypi.sh
