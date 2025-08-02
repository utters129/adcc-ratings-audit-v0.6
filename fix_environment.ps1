# PowerShell Environment Fix Script for ADCC Project
# This script fixes PATH issues and runs Python commands

Write-Host "Fixing environment..." -ForegroundColor Green

# Add Python to PATH
$pythonPaths = @(
    "C:\Users\Heath\AppData\Local\Programs\Python\Python39",
    "C:\Users\Heath\AppData\Local\Programs\Python\Python39\Scripts",
    "C:\Users\Heath\AppData\Local\Programs\Python\Python310",
    "C:\Users\Heath\AppData\Local\Programs\Python\Python310\Scripts",
    "C:\Users\Heath\AppData\Local\Programs\Python\Python311",
    "C:\Users\Heath\AppData\Local\Programs\Python\Python311\Scripts"
)

# Add Git to PATH
$gitPaths = @(
    "C:\Program Files\Git\bin",
    "C:\Program Files\Git\usr\bin",
    "C:\Program Files\Git\mingw64\bin"
)

# Update PATH
$env:PATH = ($pythonPaths + $gitPaths + $env:PATH.Split(';') | Select-Object -Unique) -join ';'

Write-Host "Environment fixed!" -ForegroundColor Green
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "- python tests/verify_phase4.py"
Write-Host "- python -m pytest tests/"
Write-Host "- python main.py"
Write-Host ""
Write-Host "Type your command:" -ForegroundColor Cyan
$command = Read-Host
Invoke-Expression $command 