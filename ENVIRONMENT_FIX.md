# Environment Fix Guide

## Problem
The Git Bash shell has corrupted PATH and missing basic commands (`python`, `sed`, `ls`, etc.).

## Permanent Solutions

### Solution 1: Fix Git Bash (Recommended)

1. **Source the .bashrc file** (temporary fix):
   ```bash
   source ~/.bashrc
   ```

2. **Make it permanent** - Add to your Git Bash profile:
   ```bash
   echo "source ~/.bashrc" >> ~/.bash_profile
   ```

3. **Restart Git Bash** and test:
   ```bash
   python --version
   ls
   ```

### Solution 2: Use Windows Command Prompt

1. **Open Command Prompt** (not Git Bash)
2. **Navigate to project**:
   ```cmd
   cd "H:\My Drive\Projects\ADCC Ratings and Audit\v0.6"
   ```
3. **Run the fix script**:
   ```cmd
   fix_environment.bat
   ```
4. **Or run directly**:
   ```cmd
   python tests/verify_phase4.py
   ```

### Solution 3: Use PowerShell

1. **Open PowerShell**
2. **Navigate to project**:
   ```powershell
   cd "H:\My Drive\Projects\ADCC Ratings and Audit\v0.6"
   ```
3. **Run the fix script**:
   ```powershell
   .\fix_environment.ps1
   ```
4. **Or run directly**:
   ```powershell
   python tests/verify_phase4.py
   ```

### Solution 4: Use VS Code Terminal

1. **Open VS Code**
2. **Open Terminal** (Ctrl+`)
3. **Change terminal type**:
   - Click the dropdown next to the terminal
   - Select "Command Prompt" or "PowerShell"
4. **Run commands**:
   ```cmd
   python tests/verify_phase4.py
   ```

## Quick Commands to Test

After fixing the environment, test with:

```bash
# Test Python
python --version
python -c "print('Hello World')"

# Test basic commands
ls
pwd
which python

# Test project commands
python tests/verify_phase4.py
python -m pytest tests/ -v
```

## If Still Having Issues

1. **Check Python installation**:
   ```cmd
   where python
   dir "C:\Users\Heath\AppData\Local\Programs\Python"
   ```

2. **Reinstall Git Bash** if needed
3. **Use Windows native terminals** instead of Git Bash

## Recommended Workflow

For this project, I recommend using **Windows Command Prompt** or **PowerShell** instead of Git Bash to avoid these issues permanently. 