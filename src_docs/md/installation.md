# Installation Guide

Comprehensive installation instructions for `claif_gem` across all platforms and environments. Choose the installation method that best fits your needs.

## 📋 System Requirements

### Minimum Requirements

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **Python** | 3.12+ | Tested on 3.12, 3.13 |
| **Node.js** | 18+ | For Gemini CLI (alternative: Bun) |
| **Operating System** | Windows 10+, macOS 12+, Linux | Cross-platform support |
| **Memory** | 512MB RAM | For basic operations |
| **Disk Space** | 100MB | Including dependencies |

### Recommended Setup

| Component | Recommendation | Benefits |
|-----------|----------------|----------|
| **Python** | 3.13+ | Latest features and performance |
| **Package Manager** | uv or pip | uv is faster for dependency management |
| **Node.js Alternative** | Bun | 10x faster than npm installations |
| **Memory** | 2GB+ RAM | For larger model contexts |
| **Disk Space** | 500MB+ | For development dependencies |

## 🎯 Quick Installation

### Standard Installation

=== "Using pip"

    ```bash
    pip install claif_gem
    ```

=== "Using uv (Faster)"

    ```bash
    # Install uv if not already installed
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Install claif_gem
    uv pip install claif_gem
    ```

=== "Using pipx (Isolated)"

    ```bash
    # Install pipx if not already installed
    pip install pipx
    
    # Install claif_gem in isolated environment
    pipx install claif_gem
    ```

### Gemini CLI Installation

The Gemini CLI is required for `claif_gem` to function. Choose your preferred method:

=== "npm (Standard)"

    ```bash
    npm install -g @google/gemini-cli
    ```

=== "Bun (Recommended)"

    ```bash
    # Install Bun
    curl -fsSL https://bun.sh/install | bash
    source ~/.bashrc  # or restart terminal
    
    # Install Gemini CLI
    bun add -g @google/gemini-cli
    ```

=== "Yarn"

    ```bash
    yarn global add @google/gemini-cli
    ```

=== "pnpm"

    ```bash
    pnpm add -g @google/gemini-cli
    ```

## 🔧 Installation Options

### Development Installation

For contributors and developers who want to modify the code:

```bash
# Clone the repository
git clone https://github.com/twardoch/claif_gem.git
cd claif_gem

# Install in development mode with all dependencies
pip install -e ".[dev,test,docs]"

# Or using uv
uv pip install -e ".[dev,test,docs]"
```

### Production Installation

For production environments with minimal dependencies:

```bash
# Core package only
pip install claif_gem

# With specific extras
pip install "claif_gem[all]"  # All optional dependencies
```

### Virtual Environment Setup

=== "venv (Standard)"

    ```bash
    # Create virtual environment
    python -m venv claif_gem_env
    
    # Activate (Linux/macOS)
    source claif_gem_env/bin/activate
    
    # Activate (Windows)
    claif_gem_env\Scripts\activate
    
    # Install claif_gem
    pip install claif_gem
    ```

=== "uv (Modern)"

    ```bash
    # Create and activate virtual environment
    uv venv --python 3.12
    source .venv/bin/activate  # Linux/macOS
    # or .venv\Scripts\activate  # Windows
    
    # Install claif_gem
    uv pip install claif_gem
    ```

=== "conda"

    ```bash
    # Create conda environment
    conda create -n claif_gem python=3.12
    conda activate claif_gem
    
    # Install claif_gem
    pip install claif_gem
    ```

## 🌍 Platform-Specific Instructions

### Windows

=== "PowerShell (Recommended)"

    ```powershell
    # Install Python (if not installed)
    winget install Python.Python.3.12
    
    # Install Node.js or Bun
    winget install OpenJS.NodeJS
    # or
    irm bun.sh/install.ps1 | iex
    
    # Install claif_gem
    pip install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    # or
    bun add -g @google/gemini-cli
    ```

=== "Command Prompt"

    ```cmd
    # Install claif_gem
    pip install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    ```

=== "Windows Subsystem for Linux (WSL)"

    ```bash
    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Install Python and pip
    sudo apt install python3.12 python3-pip
    
    # Install Node.js
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    # Install claif_gem
    pip install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    ```

### macOS

=== "Homebrew (Recommended)"

    ```bash
    # Install Homebrew if not installed
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Install Python
    brew install python@3.12
    
    # Install Node.js or Bun
    brew install node
    # or
    brew install bun
    
    # Install claif_gem
    pip3 install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    # or
    bun add -g @google/gemini-cli
    ```

=== "MacPorts"

    ```bash
    # Install Python
    sudo port install python312
    
    # Install Node.js
    sudo port install nodejs20
    
    # Install claif_gem
    pip3.12 install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    ```

=== "Manual Installation"

    ```bash
    # Download and install Python from python.org
    # Download and install Node.js from nodejs.org
    
    # Install claif_gem
    pip3 install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    ```

### Linux

=== "Ubuntu/Debian"

    ```bash
    # Update package list
    sudo apt update
    
    # Install Python and pip
    sudo apt install python3.12 python3-pip python3.12-venv
    
    # Install Node.js
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    
    # Or install Bun
    curl -fsSL https://bun.sh/install | bash
    
    # Install claif_gem
    pip install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    # or
    bun add -g @google/gemini-cli
    ```

=== "Red Hat/CentOS/Fedora"

    ```bash
    # For Fedora
    sudo dnf install python3.12 python3-pip nodejs npm
    
    # For CentOS/RHEL (enable EPEL first)
    sudo yum install epel-release
    sudo yum install python3.12 python3-pip nodejs npm
    
    # Install claif_gem
    pip install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    ```

=== "Arch Linux"

    ```bash
    # Install dependencies
    sudo pacman -S python python-pip nodejs npm
    
    # Or install Bun
    yay -S bun
    
    # Install claif_gem
    pip install claif_gem
    
    # Install Gemini CLI
    npm install -g @google/gemini-cli
    # or
    bun add -g @google/gemini-cli
    ```

## 🐳 Docker Installation

### Using Official Image (Coming Soon)

```dockerfile
# Use official Python image
FROM python:3.12-slim

# Install Node.js
RUN apt-get update && apt-get install -y nodejs npm

# Install claif_gem
RUN pip install claif_gem

# Install Gemini CLI
RUN npm install -g @google/gemini-cli

# Set environment variables
ENV GEMINI_API_KEY=""

# Create app directory
WORKDIR /app

# Default command
CMD ["python", "-c", "import claif_gem; print('claif_gem is ready!')"]
```

### Custom Dockerfile

```dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install Bun (optional, faster alternative)
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:$PATH"

# Install claif_gem
RUN pip install claif_gem

# Install Gemini CLI
RUN bun add -g @google/gemini-cli

# Set working directory
WORKDIR /app

# Copy your application
COPY . .

# Set environment variables
ENV GEMINI_API_KEY=""
ENV GEMINI_CLI_PATH="/root/.bun/bin/gemini"

# Run your application
CMD ["python", "your_app.py"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  claif-gem:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./app:/app
    working_dir: /app
    command: python main.py
```

## ☁️ Cloud Platform Installation

### Google Cloud Platform

```bash
# Using Cloud Shell
gcloud cloud-shell ssh

# Install claif_gem
pip install claif_gem

# Install Gemini CLI
npm install -g @google/gemini-cli

# Set API key from Secret Manager
export GEMINI_API_KEY=$(gcloud secrets versions access latest --secret="gemini-api-key")
```

### AWS

```bash
# Using AWS Cloud9 or EC2
sudo yum update -y
sudo yum install -y python3 python3-pip nodejs npm

pip install claif_gem
npm install -g @google/gemini-cli

# Set API key from AWS Secrets Manager
export GEMINI_API_KEY=$(aws secretsmanager get-secret-value --secret-id gemini-api-key --query SecretString --output text)
```

### Azure

```bash
# Using Azure Cloud Shell
pip install claif_gem
npm install -g @google/gemini-cli

# Set API key from Azure Key Vault
export GEMINI_API_KEY=$(az keyvault secret show --name gemini-api-key --vault-name your-vault --query value -o tsv)
```

## 🔧 Post-Installation Configuration

### API Key Setup

=== "Environment Variable (Recommended)"

    ```bash
    # Linux/macOS
    echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
    source ~/.bashrc
    
    # Windows PowerShell
    [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-api-key-here", "User")
    ```

=== "Configuration File"

    Create `~/.claif/config.json`:
    ```json
    {
      "providers": {
        "gemini": {
          "api_key": "your-api-key-here",
          "default_model": "gemini-1.5-flash",
          "timeout": 120
        }
      }
    }
    ```

=== "In Code"

    ```python
    from claif_gem import GeminiClient
    
    # Pass directly to client
    client = GeminiClient(api_key="your-api-key-here")
    ```

### CLI Path Configuration

If the Gemini CLI is installed in a non-standard location:

```bash
# Set CLI path
export GEMINI_CLI_PATH="/custom/path/to/gemini"

# Or in configuration file
```

```json
{
  "providers": {
    "gemini": {
      "cli_path": "/custom/path/to/gemini"
    }
  }
}
```

## ✅ Installation Verification

### Basic Verification

```python
# Test basic import
import claif_gem
print(f"claif_gem version: {claif_gem.__version__}")

# Test client creation
from claif_gem import GeminiClient
client = GeminiClient()
print("✅ Client created successfully")
```

### Full Verification

```python
from claif_gem import GeminiClient

def verify_installation():
    try:
        # Test client initialization
        client = GeminiClient()
        print("✅ Client initialized")
        
        # Test API call
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        print("✅ API call successful")
        print(f"Response: {response.choices[0].message.content}")
        
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    verify_installation()
```

### CLI Verification

```bash
# Test claif_gem CLI
claif-gem --help

# Test basic query
claif-gem query "Hello!" --show-metrics

# Test configuration
claif-gem config show

# Test model listing
claif-gem models
```

## 🚨 Troubleshooting

### Common Installation Issues

!!! error "Python Version Error"
    ```
    ERROR: Package requires Python 3.12 or higher
    ```
    
    **Solution:** Upgrade Python or use pyenv:
    ```bash
    # Using pyenv
    pyenv install 3.12.0
    pyenv global 3.12.0
    ```

!!! error "Gemini CLI Not Found"
    ```
    FileNotFoundError: Gemini CLI not found
    ```
    
    **Solutions:**
    ```bash
    # Check if installed
    which gemini
    
    # Reinstall if missing
    npm install -g @google/gemini-cli
    
    # Set custom path
    export GEMINI_CLI_PATH="/path/to/gemini"
    ```

!!! error "Permission Denied"
    ```
    PermissionError: [Errno 13] Permission denied
    ```
    
    **Solutions:**
    ```bash
    # For npm global installs
    npm config set prefix ~/.npm-global
    export PATH=~/.npm-global/bin:$PATH
    
    # For pip user installs
    pip install --user claif_gem
    
    # Fix CLI permissions
    chmod +x $(which gemini)
    ```

!!! error "Node.js Version Conflict"
    ```
    Error: Requires Node.js 18.0.0 or higher
    ```
    
    **Solutions:**
    ```bash
    # Using nvm
    nvm install 20
    nvm use 20
    
    # Using n
    npm install -g n
    n latest
    ```

### Platform-Specific Issues

=== "Windows"

    **PowerShell Execution Policy:**
    ```powershell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
    
    **Long Path Support:**
    ```cmd
    # Enable long paths in registry
    reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1
    ```

=== "macOS"

    **Xcode Command Line Tools:**
    ```bash
    xcode-select --install
    ```
    
    **Permission Issues:**
    ```bash
    sudo chown -R $(whoami) $(npm config get prefix)/{lib/node_modules,bin,share}
    ```

=== "Linux"

    **Missing Build Dependencies:**
    ```bash
    # Ubuntu/Debian
    sudo apt install build-essential python3-dev
    
    # CentOS/RHEL
    sudo yum groupinstall "Development Tools"
    sudo yum install python3-devel
    ```

### Network Issues

!!! warning "Corporate Firewall"
    If behind a corporate firewall:
    ```bash
    # Set npm proxy
    npm config set proxy http://proxy.company.com:8080
    npm config set https-proxy http://proxy.company.com:8080
    
    # Set pip proxy
    pip install --proxy http://proxy.company.com:8080 claif_gem
    ```

!!! warning "SSL Certificate Issues"
    ```bash
    # Disable SSL verification (not recommended for production)
    npm config set strict-ssl false
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org claif_gem
    ```

## 🔄 Upgrading

### Upgrade claif_gem

```bash
# Upgrade to latest version
pip install --upgrade claif_gem

# Upgrade to specific version
pip install claif_gem==1.0.30

# Using uv
uv pip install --upgrade claif_gem
```

### Upgrade Gemini CLI

```bash
# Using npm
npm update -g @google/gemini-cli

# Using Bun
bun update -g @google/gemini-cli

# Check current version
gemini --version
```

### Migration Guide

When upgrading between major versions, check the [CHANGELOG.md](https://github.com/twardoch/claif_gem/blob/main/CHANGELOG.md) for breaking changes.

## 🗑️ Uninstallation

### Remove claif_gem

```bash
# Uninstall package
pip uninstall claif_gem

# Remove configuration (optional)
rm -rf ~/.claif

# Remove virtual environment (if used)
rm -rf claif_gem_env
```

### Remove Gemini CLI

```bash
# Using npm
npm uninstall -g @google/gemini-cli

# Using Bun
bun remove -g @google/gemini-cli

# Clean npm cache
npm cache clean --force
```

## ⏭️ Next Steps

After successful installation:

1. **[Quick Start Guide](quickstart.md)** - Get started in 5 minutes
2. **[Usage Guide](usage.md)** - Learn comprehensive usage patterns
3. **[Configuration](configuration.md)** - Customize your setup
4. **[CLI Reference](cli-reference.md)** - Master the command-line interface

---

**Need help?** Join our [discussions](https://github.com/twardoch/claif_gem/discussions) or [open an issue](https://github.com/twardoch/claif_gem/issues).