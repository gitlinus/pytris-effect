#!/usr/bin/env bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
deactivate || conda deactivate || source deactivate
