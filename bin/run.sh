#!/bin/bash
script_dir=`dirname $0`
echo "Changing to parent of script directory: $script_dir"
cd $script_dir/..
source gwfjtenv/bin/activate
python3 main.py
deactivate
cd -