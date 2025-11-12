@echo off
REM Script to manage Python virtual environment for the backend

IF "%1"=="create" (
    echo Creating Python virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -e .[dev]
    echo Virtual environment created and packages installed!
    goto :eof
)

IF "%1"=="activate" (
    echo Activating virtual environment...
    call venv\Scripts\activate
    echo Virtual environment activated!
    goto :eof
)

IF "%1"=="deactivate" (
    echo Deactivating virtual environment...
    call venv\Scripts\deactivate
    echo Virtual environment deactivated!
    goto :eof
)

IF "%1"=="install" (
    call venv\Scripts\activate
    echo Installing packages...
    pip install -e .[dev]
    echo Packages installed!
    goto :eof
)

IF "%1"=="test" (
    call venv\Scripts\activate
    echo Running tests...
    python -m pytest --cov
    goto :eof
)

IF "%1"=="run" (
    call venv\Scripts\activate
    echo Starting backend server...
    uvicorn main:app --reload
    goto :eof
)

echo Usage:
echo env.bat create    - Create new virtual environment and install packages
echo env.bat activate  - Activate virtual environment
echo env.bat deactivate - Deactivate virtual environment
echo env.bat install   - Install/update packages
echo env.bat test      - Run tests with coverage
echo env.bat run       - Start backend server