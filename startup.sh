#!/bin/bash

cd "$(dirname "$0")"

echo ">> INSTALLING REQUIREMENTS..."
pip3 install -U -r requirements.txt

echo ">> STARTING MUSIC PLAYER..."
echo ""
echo "========================================"
echo "        MUSIC PLAYER"
echo "        SUCCESSFULLY DEPLOYED!"
echo "========================================"
echo ""

python3 main.py
