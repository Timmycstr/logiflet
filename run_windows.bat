@echo off
echo [INFO] Checking and installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies. Please check your Python installation.
    pause
    exit /b
)

echo [INFO] Starting Logisim Clone...
python main.py
if %errorlevel% neq 0 (
    echo [ERROR] Application crashed.
    pause
)
