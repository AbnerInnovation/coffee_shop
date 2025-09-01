@echo off
echo Setting up Coffee Shop Backend...

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not in PATH. Please install Python 3.8+ and add it to your PATH.
    pause
    exit /b 1
)

python --version

REM Create and activate virtual environment
echo Creating virtual environment...
python -m venv venv

REM Install dependencies
echo Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

REM Set up database
echo Setting up database...
alembic upgrade head

echo.
echo Setup complete! Start the backend with:
echo   call venv\Scripts\activate.bat
echo   uvicorn app.main:app --reload
echo.
pause
