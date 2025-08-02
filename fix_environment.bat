@echo off
REM Environment Fix Script for ADCC Project
REM This script fixes PATH issues and runs Python commands

echo Fixing environment...

REM Add Python to PATH
set PATH=%PATH%;C:\Users\Heath\AppData\Local\Programs\Python\Python39
set PATH=%PATH%;C:\Users\Heath\AppData\Local\Programs\Python\Python39\Scripts
set PATH=%PATH%;C:\Users\Heath\AppData\Local\Programs\Python\Python310
set PATH=%PATH%;C:\Users\Heath\AppData\Local\Programs\Python\Python310\Scripts
set PATH=%PATH%;C:\Users\Heath\AppData\Local\Programs\Python\Python311
set PATH=%PATH%;C:\Users\Heath\AppData\Local\Programs\Python\Python311\Scripts

REM Add Git to PATH
set PATH=%PATH%;C:\Program Files\Git\bin
set PATH=%PATH%;C:\Program Files\Git\usr\bin
set PATH=%PATH%;C:\Program Files\Git\mingw64\bin

echo Environment fixed!
echo.
echo Available commands:
echo - python tests/verify_phase4.py
echo - python -m pytest tests/
echo - python main.py
echo.
echo Type your command:
set /p command=
%command%
pause 