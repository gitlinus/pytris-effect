#!/usr/bin/env bash
python3 -m venv .venv
source .venv/bin/activate

if [ "$(uname)" == "Darwin" ]; then
    python3 -m pip install -r requirements.txt    
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    sudo apt-get install -y python3-tk python3-dev

    cat requirements.txt | grep -v "pyobjc" > linux-requirements.txt
    python3 -m pip install -r linux-requirements.txt
fi


deactivate || conda deactivate || source deactivate
