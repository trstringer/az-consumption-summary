#!/bin/bash

source "SOURCE_DIR/venv/bin/activate"
python "SOURCE_DIR/az_consumption_summary.py" "$@"
deactivate
