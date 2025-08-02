# Git Bash Environment Fix
# This file fixes PATH and basic command issues

# Add standard Windows paths to PATH
export PATH="/c/Program Files/Git/bin:$PATH"
export PATH="/c/Program Files/Git/usr/bin:$PATH"
export PATH="/c/Program Files/Git/mingw64/bin:$PATH"
export PATH="/c/Windows/System32:$PATH"
export PATH="/c/Windows:$PATH"

# Add Python paths
export PATH="/c/Users/Heath/AppData/Local/Programs/Python/Python39:$PATH"
export PATH="/c/Users/Heath/AppData/Local/Programs/Python/Python39/Scripts:$PATH"
export PATH="/c/Users/Heath/AppData/Local/Programs/Python/Python310:$PATH"
export PATH="/c/Users/Heath/AppData/Local/Programs/Python/Python310/Scripts:$PATH"
export PATH="/c/Users/Heath/AppData/Local/Programs/Python/Python311:$PATH"
export PATH="/c/Users/Heath/AppData/Local/Programs/Python/Python311/Scripts:$PATH"

# Add Node.js if installed
export PATH="/c/Program Files/nodejs:$PATH"

# Add VS Code if installed
export PATH="/c/Users/Heath/AppData/Local/Programs/Microsoft VS Code/bin:$PATH"

# Set proper aliases
alias python='python3'
alias pip='pip3'

# Fix common command issues
alias ls='ls --color=auto'
alias ll='ls -la'
alias la='ls -A'

# Source this file: source ~/.bashrc 