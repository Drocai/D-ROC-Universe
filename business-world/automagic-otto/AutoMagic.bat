@echo off
title  O.T.T.O. Launcher
color 0A
cls
echo ===================================================
echo    O.T.T.O. - One-Touch To Output
echo   Automated Content Creation System
echo ===================================================
echo.
echo Checking environment setup...

:: Verify basic requirements are met
IF NOT EXIST .py (
  echo ERROR: Critical files missing. Please reinstall .
  pause
  exit /b 1
)

IF NOT EXIST .env (
  echo ERROR: No .env file found. Running setup...
  python _setup.py
  IF NOT EXIST .env (
    echo ERROR: Setup failed to create .env file.
    pause
    exit /b 1
  )
)

echo.
echo Choose an option:
echo 1. Run  (standard)
echo 2. Run  (debug mode)
echo 3. Run system verification
echo 4. Run setup
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
  echo.
  echo Starting  in standard mode...
  python run_.py
  goto end
)

if "%choice%"=="2" (
  echo.
  echo Starting  in debug mode...
  python .py --debug
  goto end
)

if "%choice%"=="3" (
  echo.
  echo Running system verification...
  python verify_all.py
  goto end
)

if "%choice%"=="4" (
  echo.
  echo Running setup...
  python _setup.py
  goto end
)

if "%choice%"=="5" (
  echo.
  echo Exiting...
  exit /b 0
)

echo Invalid choice. Please try again.

:end
echo.
echo Operation complete.
pause
