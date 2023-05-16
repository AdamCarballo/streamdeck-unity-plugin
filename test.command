#!/bin/sh
cd "~/Library/Application Support/com.elgato.StreamDeck/Plugins/com.adamcarballo.unity-integration.sdPlugin"
python3 -m venv .env
. .env/bin/activate
pip3 install --upgrade pip
pip3 install -r requirements-osx.txt
export SDI_DEBUG=True
python3 "plugin/main.py" $1 $2 $3 $4 $5 $6 $7 $8
deactivate