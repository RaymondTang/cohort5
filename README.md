# Venturenix Next-Gen AI Development Class Cohort #5

## Lesson 03 - Python Environment Setup

### Prerequisites
- macOS system
- Terminal access
- Internet connection

### Mac Installation Sequence

#### 1. Install Homebrew
First, install Homebrew (the missing package manager for macOS):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install XZ Compression Library
Install the XZ compression library required for Python compilation:
```bash
brew install xz
```

#### 3. Install pyenv
Install pyenv (Python version manager) using Homebrew:
```bash
brew install pyenv
```

#### 4. Configure Shell Environment
Add pyenv to your shell configuration:
```bash
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
```

Reload your shell configuration:
```bash
source ~/.zshrc
```

#### 5. Install Python 3.12
Install the latest Python 3.12 version using pyenv:
```bash
pyenv install 3.12
```

#### 6. Set Python 3.12 as Global Default
Activate Python 3.12 as your global Python version:
```bash
pyenv global 3.12
```

Verify the installation:
```bash
python --version
```

#### 7. Install Visual Studio Code
Install VS Code using Homebrew:
```bash
brew install --cask visual-studio-code
```

#### 8. Configure Git
Set up your Git username and email:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Verification
Verify your setup by running:
```bash
python --version
pyenv version
git config --global user.name
git config --global user.email
```

### Troubleshooting
- If you encounter permission issues, ensure you have admin privileges
- If pyenv commands are not found, restart your terminal or run `source ~/.zshrc`
- For Python installation issues, ensure you have the latest Xcode command line tools: `xcode-select --install`

### Windows Installation Sequence

#### Prerequisites
- Windows 10/11 system
- PowerShell or Command Prompt access
- Internet connection
- Administrator privileges

#### 1. Install Windows Terminal
Install Windows Terminal using winget:
```powershell
winget install Microsoft.WindowsTerminal
```

#### 2. Install Git
Install Git for Windows using winget:
```powershell
winget install Git.Git
```

After installation, restart your terminal or open a new PowerShell window to ensure Git is in your PATH.

#### 3. Install pyenv-win
Install pyenv-win (Python version manager for Windows) using the official PowerShell installer:
```powershell
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
```

This will automatically:
- Download and install pyenv-win to `%USERPROFILE%\.pyenv\pyenv-win`
- Configure the necessary environment variables
- Add pyenv to your PATH

Restart your terminal or open a new PowerShell window to ensure pyenv is available.

#### 4. Install Python 3.12
Install the latest Python 3.12 version using pyenv:
```powershell
pyenv install 3.12
```

#### 5. Set Python 3.12 as Global Default
Activate Python 3.12 as your global Python version:
```powershell
pyenv global 3.12
```

Verify the installation:
```powershell
python --version
```

#### 6. Install Python UV
Install UV using the official installer:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 7. Install Visual Studio Code
Install VS Code using winget:
```powershell
winget install Microsoft.VisualStudioCode
```

#### 8. Configure Git
Set up your Git username and email:
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Verification
Verify your setup by running:
```powershell
python --version
pyenv version
git config --global user.name
git config --global user.email
uv --version
```

### Troubleshooting
- If you encounter permission issues, ensure you're running PowerShell as Administrator
- If pyenv commands are not found, restart your terminal or check your PATH environment variable
- For Python installation issues, ensure Windows Defender or antivirus isn't blocking the installation
- If winget is not available, install it from the Microsoft Store or download from GitHub