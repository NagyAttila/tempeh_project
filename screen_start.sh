#!/bin/bash
python3 ~root/tempeh_project/regulator.py | tee ~/tempeh_project/auto_logs/`date +%Y%m%d_%H%M`.csv
