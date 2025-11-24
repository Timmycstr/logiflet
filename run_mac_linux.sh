#!/bin/bash

echo "[INFO] Checking and installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies. Please check your Python installation."
    exit 1
fi

echo "[INFO] Starting Logisim Clone..."
python3 main.py
