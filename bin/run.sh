#!/usr/bin/env bash
cd ..

config_path=`pwd`
export MSVM_APPLICATION_SETTINGS="${config_path}/app/config/local-production.py"

python runserver.py
