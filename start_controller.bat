@echo off
title Smart Traffic Compiler - Smartphone Controller Server
cls
echo ================================================================
echo    SMART TRAFFIC COMPILER - SMARTPHONE SPEED CONTROLLER
echo ================================================================
echo.

:: Detect Python location
set "PYTHON_EXE="

if exist "C:\msys64\ucrt64\bin\python.exe" (
    set "PYTHON_EXE=C:\msys64\ucrt64\bin\python.exe"
) else (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>&1
        if %errorlevel% equ 0 (
            set "PYTHON_EXE=py"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python not found on your system!
    echo Please make sure Python or MSYS2 Python is installed.
    pause
    exit /b 1
)

echo Starting Flask Controller Server using %PYTHON_EXE%...
echo.
"%PYTHON_EXE%" "%~dp0controller\app.py"

pause
