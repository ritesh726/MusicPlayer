#!/bin/bash

echo ">> INSTALLING REQUIREMENTS..."
pip3 install -U -r "$(pwd)/requirements.txt"

echo ">> STARTING MUSIC PLAYER..."
echo ""
echo "========================================"
echo "        MUSIC PLAYER"
echo "        SUCCESSFULLY DEPLOYED!"
echo "========================================"
echo ""

python3 "$(pwd)/main.py"
