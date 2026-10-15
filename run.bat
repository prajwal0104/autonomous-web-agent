@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Creating virtual environment...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    playwright install chromium
)

echo Starting Autonomous Web Agent...
echo.
.venv\Scripts\python.exe -m src.main %*
pause
