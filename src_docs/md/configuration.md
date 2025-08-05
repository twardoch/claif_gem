# Configuration Guide

Comprehensive guide to configuring `claif_gem` through environment variables, configuration files, and runtime options. Master all configuration methods and customization options.

## 🎯 Configuration Overview

`claif_gem` supports multiple configuration methods with the following priority order:

1. **Runtime Parameters** - Highest priority
2. **Environment Variables** - Medium priority  
3. **Configuration Files** - Lowest priority

## 🌍 Environment Variables

### Core Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GEMINI_API_KEY` | Google API key for Gemini access | None | `AIzaSyD...` |
| `GOOGLE_API_KEY` | Alternative API key variable | None | `AIzaSyD...` |
| `GEMINI_CLI_PATH` | Custom path to Gemini CLI binary | Auto-detected | `/usr/local/bin/gemini` |
| `CLAIF_PROVIDER` | Default provider for Claif framework | None | `gemini` |

### Advanced Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `GEMINI_DEFAULT_MODEL` | Default model to use | `gemini-1.5-flash` | `gemini-1.5-pro` |
| `GEMINI_DEFAULT_TEMPERATURE` | Default temperature setting | `0.7` | `0.5` |
| `GEMINI_DEFAULT_TIMEOUT` | Default timeout in seconds | `120` | `300` |
| `GEMINI_MAX_TOKENS` | Default max tokens limit | None | `1000` |
| `GEMINI_AUTO_APPROVE` | Auto-approve CLI operations | `true` | `false` |
| `GEMINI_YES_MODE` | Enable yes-mode for all prompts | `true` | `false` |

### Setting Environment Variables

=== "Linux/macOS (Bash)"

    ```bash
    # Set for current session
    export GEMINI_API_KEY="your-api-key-here"
    export GEMINI_DEFAULT_MODEL="gemini-1.5-pro"
    export GEMINI_DEFAULT_TEMPERATURE="0.5"
    
    # Set permanently in ~/.bashrc
    echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
    echo 'export GEMINI_DEFAULT_MODEL="gemini-1.5-pro"' >> ~/.bashrc
    source ~/.bashrc
    ```

=== "Linux/macOS (Zsh)"

    ```zsh
    # Set for current session
    export GEMINI_API_KEY="your-api-key-here"
    export GEMINI_DEFAULT_MODEL="gemini-1.5-pro"
    
    # Set permanently in ~/.zshrc
    echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
    echo 'export GEMINI_DEFAULT_MODEL="gemini-1.5-pro"' >> ~/.zshrc
    source ~/.zshrc
    ```

=== "Windows (PowerShell)"

    ```powershell
    # Set for current session
    $env:GEMINI_API_KEY="your-api-key-here"
    $env:GEMINI_DEFAULT_MODEL="gemini-1.5-pro"
    
    # Set permanently (User level)
    [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-api-key-here", "User")
    [Environment]::SetEnvironmentVariable("GEMINI_DEFAULT_MODEL", "gemini-1.5-pro", "User")
    
    # Set permanently (System level - requires admin)
    [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-api-key-here", "Machine")
    ```

=== "Windows (Command Prompt)"

    ```cmd
    # Set for current session
    set GEMINI_API_KEY=your-api-key-here
    set GEMINI_DEFAULT_MODEL=gemini-1.5-pro
    
    # Set permanently
    setx GEMINI_API_KEY "your-api-key-here"
    setx GEMINI_DEFAULT_MODEL "gemini-1.5-pro"
    ```

## 📁 Configuration Files

### Main Configuration File

Default location: `~/.claif/config.json`

```json
{
  "providers": {
    "gemini": {
      "api_key": "your-api-key-here",
      "default_model": "gemini-1.5-flash",
      "temperature": 0.7,
      "max_tokens": null,
      "timeout": 120,
      "auto_approve": true,
      "yes_mode": true,
      "cli_path": null,
      "verbose": false
    }
  },
  "global": {
    "default_provider": "gemini",
    "log_level": "INFO",
    "cache_responses": false,
    "cache_ttl": 3600
  }
}
```

### Alternative Configuration Locations

`claif_gem` searches for configuration files in this order:

1. `~/.claif/config.json`
2. `~/.config/claif/config.json`
3. `./claif.json` (project-specific)
4. `./.claif.json` (project-specific alternative)

### Creating Configuration Directory

```bash
# Create configuration directory
mkdir -p ~/.claif

# Create basic configuration file
cat > ~/.claif/config.json << 'EOF'
{
  "providers": {
    "gemini": {
      "api_key": "your-api-key-here",
      "default_model": "gemini-1.5-flash",
      "temperature": 0.7
    }
  }
}
EOF
```

## ⚙️ Configuration Management

### Using the CLI

#### Viewing Configuration

```bash
# Show current configuration
claif-gem config show

# Show configuration with sensitive data masked
claif-gem config show --mask-secrets

# Show only Gemini provider configuration
claif-gem config show --provider gemini

# Show configuration in JSON format
claif-gem config show --format json
```

#### Setting Configuration Values

```bash
# Set default model
claif-gem config set default-model gemini-1.5-pro

# Set temperature
claif-gem config set temperature 0.5

# Set timeout
claif-gem config set timeout 180

# Set auto-approve mode
claif-gem config set auto-approve false

# Set API key (will be prompted for input)
claif-gem config set api-key

# Set multiple values at once
claif-gem config set \
  default-model gemini-1.5-pro \
  temperature 0.5 \
  timeout 180
```

#### Managing Configuration Files

```bash
# Initialize new configuration file
claif-gem config init

# Initialize with custom path
claif-gem config init --path ~/.config/claif/config.json

# Validate configuration
claif-gem config validate

# Reset to defaults
claif-gem config reset

# Reset specific provider
claif-gem config reset --provider gemini

# Import configuration from file
claif-gem config import config.json

# Export configuration to file
claif-gem config export my-config.json
```

### Programmatic Configuration

#### Using Python API

```python
from claif_gem import GeminiClient
from claif_gem.config import GeminiConfig

# Create configuration object
config = GeminiConfig(
    api_key="your-api-key",
    default_model="gemini-1.5-pro",
    temperature=0.5,
    max_tokens=1000,
    timeout=180,
    auto_approve=True,
    yes_mode=True,
    verbose=False
)

# Initialize client with configuration
client = GeminiClient(config=config)

# Or pass parameters directly
client = GeminiClient(
    api_key="your-api-key",
    default_model="gemini-1.5-pro",
    timeout=180
)
```

#### Configuration Class

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class GeminiConfig:
    """Configuration class for Gemini client."""
    
    # Authentication
    api_key: Optional[str] = None
    
    # Model settings
    default_model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    
    # CLI settings
    cli_path: Optional[str] = None
    auto_approve: bool = True
    yes_mode: bool = True
    timeout: int = 120
    
    # Behavior settings
    verbose: bool = False
    stream: bool = False
    
    # Advanced settings
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'GeminiConfig':
        """Create configuration from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})
    
    @classmethod
    def from_file(cls, file_path: str) -> 'GeminiConfig':
        """Load configuration from JSON file."""
        import json
        from pathlib import Path
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")
        
        with open(path, 'r') as f:
            config_data = json.load(f)
        
        # Extract Gemini provider configuration
        gemini_config = config_data.get('providers', {}).get('gemini', {})
        return cls.from_dict(gemini_config)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        from dataclasses import asdict
        return asdict(self)
    
    def save_to_file(self, file_path: str):
        """Save configuration to JSON file."""
        import json
        from pathlib import Path
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        config_structure = {
            "providers": {
                "gemini": self.to_dict()
            }
        }
        
        with open(path, 'w') as f:
            json.dump(config_structure, f, indent=2)

# Usage examples
config = GeminiConfig(
    default_model="gemini-1.5-pro",
    temperature=0.5,
    timeout=300
)

# Save configuration
config.save_to_file("~/.claif/config.json")

# Load configuration
loaded_config = GeminiConfig.from_file("~/.claif/config.json")
```

## 🔧 Advanced Configuration

### Model-Specific Configuration

```json
{
  "providers": {
    "gemini": {
      "api_key": "your-api-key-here",
      "models": {
        "gemini-1.5-flash": {
          "temperature": 0.7,
          "max_tokens": 1000,
          "timeout": 60
        },
        "gemini-1.5-pro": {
          "temperature": 0.5,
          "max_tokens": 2000,
          "timeout": 180
        },
        "gemini-2.0-flash-exp": {
          "temperature": 0.8,
          "max_tokens": 1500,
          "timeout": 120
        }
      }
    }
  }
}
```

### Environment-Specific Configuration

#### Development Configuration

```json
{
  "providers": {
    "gemini": {
      "api_key": "dev-api-key",
      "default_model": "gemini-1.5-flash",
      "temperature": 0.9,
      "verbose": true,
      "timeout": 300,
      "auto_approve": false
    }
  },
  "global": {
    "log_level": "DEBUG",
    "cache_responses": true
  }
}
```

#### Production Configuration

```json
{
  "providers": {
    "gemini": {
      "api_key": "prod-api-key",
      "default_model": "gemini-1.5-pro",
      "temperature": 0.3,
      "verbose": false,
      "timeout": 120,
      "auto_approve": true,
      "retry_attempts": 5
    }
  },
  "global": {
    "log_level": "ERROR",
    "cache_responses": false
  }
}
```

### Profile-Based Configuration

```python
import os
from claif_gem.config import GeminiConfig

class ConfigManager:
    """Manage different configuration profiles."""
    
    PROFILES = {
        'development': {
            'default_model': 'gemini-1.5-flash',
            'temperature': 0.9,
            'verbose': True,
            'auto_approve': False,
            'timeout': 300
        },
        'production': {
            'default_model': 'gemini-1.5-pro',
            'temperature': 0.3,
            'verbose': False,
            'auto_approve': True,
            'timeout': 120
        },
        'creative': {
            'default_model': 'gemini-1.5-pro',
            'temperature': 0.9,
            'verbose': False,
            'auto_approve': True,
            'timeout': 180
        },
        'analytical': {
            'default_model': 'gemini-1.5-pro',
            'temperature': 0.1,
            'verbose': False,
            'auto_approve': True,
            'timeout': 240
        }
    }
    
    @classmethod
    def get_config(cls, profile: str = None) -> GeminiConfig:
        """Get configuration for specified profile."""
        # Determine profile
        if profile is None:
            profile = os.getenv('CLAIF_PROFILE', 'development')
        
        if profile not in cls.PROFILES:
            raise ValueError(f"Unknown profile: {profile}")
        
        # Get base configuration
        base_config = GeminiConfig()
        
        # Apply profile overrides
        profile_config = cls.PROFILES[profile]
        for key, value in profile_config.items():
            if hasattr(base_config, key):
                setattr(base_config, key, value)
        
        return base_config

# Usage
# Set profile via environment variable
os.environ['CLAIF_PROFILE'] = 'production'
config = ConfigManager.get_config()

# Or specify profile directly
creative_config = ConfigManager.get_config('creative')
```

## 🔒 Security Configuration

### API Key Security

#### Secure Storage Options

=== "Environment Variables (Recommended)"

    ```bash
    # Store in environment (most secure for production)
    export GEMINI_API_KEY="your-api-key"
    ```

=== "Configuration File with Restricted Permissions"

    ```bash
    # Create config file with restricted permissions
    touch ~/.claif/config.json
    chmod 600 ~/.claif/config.json  # Read/write for owner only
    
    # Edit file to add API key
    echo '{"providers": {"gemini": {"api_key": "your-api-key"}}}' > ~/.claif/config.json
    ```

=== "System Keyring (Advanced)"

    ```python
    import keyring
    from claif_gem import GeminiClient
    
    # Store API key in system keyring
    keyring.set_password("claif_gem", "api_key", "your-api-key")
    
    # Retrieve API key from keyring
    api_key = keyring.get_password("claif_gem", "api_key")
    client = GeminiClient(api_key=api_key)
    ```

=== "AWS Secrets Manager"

    ```python
    import boto3
    from claif_gem import GeminiClient
    
    def get_api_key_from_aws():
        """Retrieve API key from AWS Secrets Manager."""
        client = boto3.client('secretsmanager')
        response = client.get_secret_value(SecretId='gemini-api-key')
        return response['SecretString']
    
    # Usage
    api_key = get_api_key_from_aws()
    gemini_client = GeminiClient(api_key=api_key)
    ```

#### Security Best Practices

```python
import os
import json
from pathlib import Path

def secure_config_loader():
    """Load configuration with security checks."""
    
    # Check file permissions
    config_path = Path.home() / '.claif' / 'config.json'
    
    if config_path.exists():
        stat = config_path.stat()
        # Check if file is readable by others
        if stat.st_mode & 0o077:
            print("Warning: Configuration file has overly permissive permissions")
            print(f"Recommended: chmod 600 {config_path}")
    
    # Load configuration
    config = {}
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
    
    # Mask sensitive data in logs
    safe_config = config.copy()
    if 'providers' in safe_config and 'gemini' in safe_config['providers']:
        if 'api_key' in safe_config['providers']['gemini']:
            key = safe_config['providers']['gemini']['api_key']
            if key:
                safe_config['providers']['gemini']['api_key'] = key[:8] + '...'
    
    return config, safe_config

# Usage
config, safe_config = secure_config_loader()
print("Loaded configuration:", safe_config)
```

## 🌐 Network Configuration

### Proxy Configuration

```bash
# HTTP proxy
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# For npm (Gemini CLI installation)
npm config set proxy http://proxy.company.com:8080
npm config set https-proxy http://proxy.company.com:8080

# No proxy for certain domains
export NO_PROXY=localhost,127.0.0.1,.company.com
```

### SSL Configuration

```json
{
  "providers": {
    "gemini": {
      "ssl_verify": true,
      "ssl_cert_path": "/path/to/cert.pem",
      "ssl_key_path": "/path/to/key.pem",
      "timeout": 120
    }
  }
}
```

## 📊 Logging Configuration

### Log Level Configuration

```json
{
  "global": {
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": "~/.claif/logs/claif_gem.log",
    "max_log_size": 10485760,
    "backup_count": 5
  }
}
```

### Environment-Based Logging

```bash
# Set log level via environment
export CLAIF_LOG_LEVEL=DEBUG
export CLAIF_LOG_FILE=/var/log/claif_gem.log

# Enable verbose logging
export GEMINI_VERBOSE=true
```

### Custom Logging Configuration

```python
import logging
from claif_gem import GeminiClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claif_gem.log'),
        logging.StreamHandler()
    ]
)

# Enable debug logging for claif_gem
logger = logging.getLogger('claif_gem')
logger.setLevel(logging.DEBUG)

# Use client with logging
client = GeminiClient(verbose=True)
```

## ✅ Configuration Validation

### Validation Script

```python
#!/usr/bin/env python3
"""Configuration validation script for claif_gem."""

import os
import json
from pathlib import Path
from claif_gem import GeminiClient
from claif_gem.config import GeminiConfig

def validate_configuration():
    """Validate claif_gem configuration."""
    print("🔍 Validating claif_gem configuration...\n")
    
    # Check 1: API Key
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if api_key:
        print("✅ API key found in environment variables")
    else:
        print("❌ API key not found in environment variables")
        
        # Check config file
        config_path = Path.home() / '.claif' / 'config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if config.get('providers', {}).get('gemini', {}).get('api_key'):
                        print("✅ API key found in configuration file")
                    else:
                        print("❌ API key not found in configuration file")
            except Exception as e:
                print(f"❌ Error reading configuration file: {e}")
        else:
            print("❌ Configuration file not found")
    
    # Check 2: Gemini CLI
    cli_path = os.getenv('GEMINI_CLI_PATH')
    if cli_path:
        if Path(cli_path).exists():
            print(f"✅ Gemini CLI found at custom path: {cli_path}")
        else:
            print(f"❌ Gemini CLI not found at custom path: {cli_path}")
    else:
        import shutil
        cli_path = shutil.which('gemini')
        if cli_path:
            print(f"✅ Gemini CLI found in PATH: {cli_path}")
        else:
            print("❌ Gemini CLI not found in PATH")
    
    # Check 3: Client initialization
    try:
        client = GeminiClient()
        print("✅ GeminiClient initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize GeminiClient: {e}")
        return False
    
    # Check 4: API call
    try:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=10
        )
        print("✅ API call successful")
        print(f"   Response: {response.choices[0].message.content[:50]}...")
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False
    
    print("\n🎉 Configuration validation completed successfully!")
    return True

if __name__ == "__main__":
    validate_configuration()
```

### CLI Validation

```bash
# Run validation script
python validate_config.py

# Or use CLI validation
claif-gem config validate

# Test basic functionality
claif-gem query "Hello!" --show-metrics
```

## ⏭️ Next Steps

Now that you understand configuration:

1. **[CLI Reference](cli-reference.md)** - Master all command-line options
2. **[API Reference](api-reference.md)** - Detailed Python API documentation
3. **[Testing Guide](testing.md)** - Learn testing strategies and setup
4. **[Architecture Guide](architecture.md)** - Understand internal design

---

**Configuration Issues?** Check our [troubleshooting guide](installation.md#troubleshooting) or [open an issue](https://github.com/twardoch/claif_gem/issues).