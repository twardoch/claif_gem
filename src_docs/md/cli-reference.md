# CLI Reference

Complete command-line interface reference for `claif-gem`. Master all commands, options, and usage patterns for effective CLI usage.

## 🚀 Overview

The `claif-gem` CLI provides a powerful interface to interact with Google Gemini models directly from the command line. Built with Python Fire, it offers both simple commands and advanced options.

### Quick Reference

```bash
# Basic usage
claif-gem query "Your prompt here"
claif-gem chat
claif-gem models
claif-gem config show

# With options
claif-gem query "Prompt" --model gemini-1.5-pro --temperature 0.7
claif-gem chat --system "You are a helpful assistant"
```

## 📖 Command Structure

```
claif-gem <command> [arguments] [options]
```

### Global Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--help` | `-h` | Show help message | - |
| `--version` | `-v` | Show version information | - |
| `--verbose` | - | Enable verbose output | `false` |
| `--quiet` | `-q` | Suppress all output except results | `false` |
| `--json` | - | Output in JSON format | `false` |

## 🎯 Core Commands

### `query` - Single Query

Execute a single query to Gemini and display the response.

#### Syntax

```bash
claif-gem query <prompt> [options]
```

#### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `prompt` | Yes | The text prompt to send to Gemini |

#### Options

| Option | Type | Description | Default | Example |
|--------|------|-------------|---------|---------|
| `--model` | string | Model to use | `gemini-1.5-flash` | `--model gemini-1.5-pro` |
| `--temperature` | float | Sampling temperature (0.0-2.0) | `0.7` | `--temperature 0.9` |
| `--max-tokens` | int | Maximum tokens to generate | None | `--max-tokens 500` |
| `--system` | string | System prompt/instruction | None | `--system "You are a helpful assistant"` |
| `--stream` | flag | Stream the response | `false` | `--stream` |
| `--timeout` | int | Request timeout in seconds | `120` | `--timeout 300` |
| `--show-metrics` | flag | Show response metrics | `false` | `--show-metrics` |
| `--raw` | flag | Output raw response without formatting | `false` | `--raw` |

#### Examples

```bash
# Basic query
claif-gem query "What is machine learning?"

# With specific model
claif-gem query "Explain quantum computing" --model gemini-1.5-pro

# Creative writing with high temperature
claif-gem query "Write a creative story about robots" --temperature 0.9

# Code generation with system prompt
claif-gem query "Write a Python function to sort a list" \
  --system "You are an expert Python developer" \
  --temperature 0.3

# Stream long response
claif-gem query "Write a detailed tutorial on REST APIs" --stream

# With token limit
claif-gem query "Summarize the history of AI" --max-tokens 200

# Show performance metrics
claif-gem query "Hello!" --show-metrics

# Raw JSON output
claif-gem query "Hello!" --json --raw
```

### `chat` - Interactive Chat

Start an interactive chat session with continuous conversation.

#### Syntax

```bash
claif-gem chat [options]
```

#### Options

| Option | Type | Description | Default | Example |
|--------|------|-------------|---------|---------|
| `--model` | string | Model to use for chat | `gemini-1.5-flash` | `--model gemini-1.5-pro` |
| `--temperature` | float | Sampling temperature | `0.7` | `--temperature 0.8` |
| `--system` | string | System prompt for the session | None | `--system "You are a coding tutor"` |
| `--max-tokens` | int | Max tokens per response | None | `--max-tokens 1000` |
| `--timeout` | int | Timeout per request | `120` | `--timeout 180` |
| `--save-history` | string | Save chat history to file | None | `--save-history chat.json` |
| `--load-history` | string | Load previous chat history | None | `--load-history chat.json` |

#### Chat Commands

Within the chat session, use these special commands:

| Command | Description |
|---------|-------------|
| `/help` | Show chat help |
| `/clear` | Clear conversation history |
| `/save <file>` | Save current conversation |
| `/load <file>` | Load conversation from file |
| `/model <name>` | Switch model |
| `/temp <value>` | Set temperature |
| `/system <prompt>` | Set system prompt |
| `/exit` or `/quit` | Exit chat session |

#### Examples

```bash
# Basic interactive chat
claif-gem chat

# Chat with specific model and system prompt
claif-gem chat --model gemini-1.5-pro --system "You are a helpful Python tutor"

# Creative writing session
claif-gem chat --temperature 0.9 --system "You are a creative writing assistant"

# Load previous conversation
claif-gem chat --load-history previous_session.json

# Chat with custom settings
claif-gem chat \
  --model gemini-1.5-pro \
  --temperature 0.5 \
  --max-tokens 500 \
  --timeout 180
```

### `models` - List Available Models

Display information about available Gemini models.

#### Syntax

```bash
claif-gem models [options]
```

#### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `--detailed` | flag | Show detailed model information | `false` |
| `--json` | flag | Output in JSON format | `false` |
| `--filter` | string | Filter models by name pattern | None |

#### Examples

```bash
# List all models
claif-gem models

# Detailed model information
claif-gem models --detailed

# JSON output
claif-gem models --json

# Filter models
claif-gem models --filter "1.5"
```

### `config` - Configuration Management

Manage configuration settings for claif-gem.

#### Syntax

```bash
claif-gem config <subcommand> [options]
```

#### Subcommands

##### `show` - Display Configuration

```bash
claif-gem config show [options]
```

**Options:**
- `--mask-secrets`: Hide sensitive information
- `--provider <name>`: Show specific provider config
- `--format <format>`: Output format (table, json, yaml)

**Examples:**
```bash
claif-gem config show
claif-gem config show --mask-secrets
claif-gem config show --provider gemini --format json
```

##### `set` - Set Configuration Values

```bash
claif-gem config set <key> <value> [options]
```

**Available Keys:**
- `api-key`: API key for Gemini
- `default-model`: Default model to use
- `temperature`: Default temperature
- `timeout`: Default timeout
- `auto-approve`: Auto-approve CLI operations
- `verbose`: Enable verbose logging

**Examples:**
```bash
claif-gem config set default-model gemini-1.5-pro
claif-gem config set temperature 0.5
claif-gem config set timeout 180
claif-gem config set auto-approve false
```

##### `get` - Get Configuration Value

```bash
claif-gem config get <key>
```

**Examples:**
```bash
claif-gem config get default-model
claif-gem config get temperature
```

##### `unset` - Remove Configuration Value

```bash
claif-gem config unset <key>
```

**Examples:**
```bash
claif-gem config unset temperature
claif-gem config unset timeout
```

##### `init` - Initialize Configuration

```bash
claif-gem config init [options]
```

**Options:**
- `--path <path>`: Custom config file path
- `--force`: Overwrite existing configuration

**Examples:**
```bash
claif-gem config init
claif-gem config init --path ~/.config/claif/config.json
claif-gem config init --force
```

##### `validate` - Validate Configuration

```bash
claif-gem config validate
```

##### `reset` - Reset Configuration

```bash
claif-gem config reset [options]
```

**Options:**
- `--provider <name>`: Reset specific provider
- `--confirm`: Skip confirmation prompt

### `version` - Version Information

Display version information for claif-gem and dependencies.

#### Syntax

```bash
claif-gem version [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `--detailed` | Show detailed version information |
| `--check-updates` | Check for available updates |
| `--json` | Output in JSON format |

#### Examples

```bash
# Basic version info
claif-gem version

# Detailed version info
claif-gem version --detailed

# Check for updates
claif-gem version --check-updates

# JSON output
claif-gem version --json
```

### `health` - Health Check

Perform system health checks and diagnostics.

#### Syntax

```bash
claif-gem health [options]
```

#### Options

| Option | Description |
|--------|-------------|
| `--verbose` | Show detailed diagnostic information |
| `--fix` | Attempt to fix detected issues |
| `--json` | Output results in JSON format |

#### Examples

```bash
# Basic health check
claif-gem health

# Verbose health check
claif-gem health --verbose

# Try to fix issues
claif-gem health --fix

# JSON output for automation
claif-gem health --json
```

## 🔧 Advanced Usage

### Output Formatting

#### JSON Output

Most commands support `--json` flag for machine-readable output:

```bash
# Query with JSON output
claif-gem query "Hello!" --json

# Model list in JSON
claif-gem models --json

# Configuration in JSON
claif-gem config show --json

# Health check results in JSON
claif-gem health --json
```

#### Quiet Mode

Suppress all output except the essential results:

```bash
# Quiet query (only shows response)
claif-gem query "What is 2+2?" --quiet

# Quiet config get
claif-gem config get default-model --quiet
```

#### Verbose Mode

Enable detailed logging and diagnostic output:

```bash
# Verbose query
claif-gem query "Hello!" --verbose

# Verbose chat
claif-gem chat --verbose

# Verbose health check
claif-gem health --verbose
```

### Environment Integration

#### Shell Completion

Enable shell completion for better CLI experience:

=== "Bash"

    ```bash
    # Add to ~/.bashrc
    eval "$(claif-gem --completion bash)"
    
    # Or generate completion script
    claif-gem --completion bash > ~/.bash_completion.d/claif-gem
    ```

=== "Zsh"

    ```zsh
    # Add to ~/.zshrc
    eval "$(claif-gem --completion zsh)"
    
    # Or generate completion script
    claif-gem --completion zsh > ~/.zsh/completions/_claif-gem
    ```

=== "Fish"

    ```fish
    # Add to config.fish
    claif-gem --completion fish | source
    
    # Or generate completion script
    claif-gem --completion fish > ~/.config/fish/completions/claif-gem.fish
    ```

#### Aliases and Functions

Create useful aliases for common operations:

```bash
# Add to ~/.bashrc or ~/.zshrc

# Quick aliases
alias gm='claif-gem query'
alias gmc='claif-gem chat'
alias gmm='claif-gem models'

# Function for quick code generation
gmcode() {
    claif-gem query "$1" \
        --system "You are an expert programmer. Provide clean, well-commented code." \
        --temperature 0.3 \
        --model gemini-1.5-pro
}

# Function for creative writing
gmwrite() {
    claif-gem query "$1" \
        --system "You are a creative writer." \
        --temperature 0.9 \
        --stream
}

# Function for analysis
gmanalyze() {
    claif-gem query "$1" \
        --system "You are an expert analyst. Provide detailed, structured analysis." \
        --temperature 0.3 \
        --model gemini-1.5-pro
}
```

### Scripting and Automation

#### Exit Codes

`claif-gem` returns standard exit codes for automation:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid command/arguments |
| 3 | Configuration error |
| 4 | Network/API error |
| 5 | Authentication error |

#### Batch Processing Script

```bash
#!/bin/bash
# batch_query.sh - Process multiple queries

QUERIES_FILE="$1"
OUTPUT_DIR="$2"

if [ $# -ne 2 ]; then
    echo "Usage: $0 <queries_file> <output_dir>"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

while IFS= read -r query; do
    # Skip empty lines and comments
    [[ -z "$query" || "$query" =~ ^#.* ]] && continue
    
    # Generate filename from query
    filename=$(echo "$query" | tr ' ' '_' | tr -cd '[:alnum:]_' | cut -c1-50)
    
    echo "Processing: $query"
    
    # Execute query and save result
    if claif-gem query "$query" --json > "$OUTPUT_DIR/${filename}.json"; then
        echo "✅ Saved to $OUTPUT_DIR/${filename}.json"
    else
        echo "❌ Failed to process: $query"
    fi
    
    # Add delay to respect rate limits
    sleep 1
done < "$QUERIES_FILE"

echo "Batch processing complete!"
```

#### Configuration Backup Script

```bash
#!/bin/bash
# backup_config.sh - Backup claif-gem configuration

BACKUP_DIR="$HOME/.claif/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/config_backup_$TIMESTAMP.json"

mkdir -p "$BACKUP_DIR"

# Export current configuration
if claif-gem config show --json > "$BACKUP_FILE"; then
    echo "✅ Configuration backed up to: $BACKUP_FILE"
    
    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/config_backup_*.json | tail -n +11 | xargs -r rm
    echo "🧹 Old backups cleaned up"
else
    echo "❌ Failed to backup configuration"
    exit 1
fi
```

#### Health Monitoring Script

```bash
#!/bin/bash
# monitor_health.sh - Monitor claif-gem health

LOG_FILE="$HOME/.claif/health.log"

echo "$(date): Starting health check" >> "$LOG_FILE"

if claif-gem health --json > /tmp/health_result.json; then
    # Parse JSON result
    if command -v jq > /dev/null; then
        status=$(jq -r '.status' /tmp/health_result.json)
        if [ "$status" = "healthy" ]; then
            echo "$(date): Health check passed" >> "$LOG_FILE"
        else
            echo "$(date): Health check failed - $status" >> "$LOG_FILE"
            # Send alert (customize as needed)
            echo "claif-gem health check failed: $status" | mail -s "claif-gem Alert" admin@example.com
        fi
    fi
else
    echo "$(date): Health check command failed" >> "$LOG_FILE"
fi

rm -f /tmp/health_result.json
```

## 🛠️ Troubleshooting CLI Issues

### Common Problems

#### Command Not Found

```bash
# Error: command not found: claif-gem

# Solutions:
# 1. Reinstall package
pip install --force-reinstall claif-gem

# 2. Check PATH
echo $PATH
which claif-gem

# 3. Use full path
python -m claif_gem.cli query "Hello!"
```

#### Permission Denied

```bash
# Error: Permission denied

# Solutions:
# 1. Check file permissions
ls -la $(which claif-gem)

# 2. Fix permissions
chmod +x $(which claif-gem)

# 3. Install with --user flag
pip install --user claif-gem
```

#### API Key Issues

```bash
# Error: API key not found

# Check current configuration
claif-gem config show

# Set API key
claif-gem config set api-key
# Or
export GEMINI_API_KEY="your-api-key"

# Validate configuration
claif-gem config validate
```

#### Gemini CLI Not Found

```bash
# Error: Gemini CLI not found

# Check if installed
which gemini

# Install if missing
npm install -g @google/gemini-cli

# Set custom path
export GEMINI_CLI_PATH="/path/to/gemini"
# Or
claif-gem config set cli-path "/path/to/gemini"
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Enable debug logging
export CLAIF_LOG_LEVEL=DEBUG

# Run with verbose output
claif-gem query "Hello!" --verbose

# Check health with detailed output
claif-gem health --verbose
```

## ⏭️ Next Steps

Now that you've mastered the CLI:

1. **[API Reference](api-reference.md)** - Learn the Python API for programmatic use
2. **[Architecture Guide](architecture.md)** - Understand how claif-gem works internally
3. **[Testing Guide](testing.md)** - Learn testing strategies and setup
4. **[Contributing Guide](contributing.md)** - Contribute to the project

---

**CLI Questions?** Check our [discussions](https://github.com/twardoch/claif_gem/discussions) or [open an issue](https://github.com/twardoch/claif_gem/issues).