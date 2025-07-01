# CLAIF_GEM - Gemini Provider for CLAIF

CLAIF_GEM is the Gemini provider implementation for the CLAIF (Command Line Artificial Intelligence Framework). It provides a wrapper around the Gemini CLI to integrate Google's Gemini AI capabilities into the unified CLAIF ecosystem.

## What is CLAIF_GEM?

CLAIF_GEM is a specialized provider package that:
- Wraps the Gemini CLI for use with CLAIF
- Provides access to Google's Gemini language models
- Supports auto-approval and yes-mode for streamlined interactions
- Handles subprocess communication with the Gemini binary
- Offers a Fire-based CLI with rich terminal output
- Includes context management and timeout handling

## Installation

### From PyPI
```bash
pip install claif_gem
```

### From Source
```bash
git clone https://github.com/twardoch/claif_gem.git
cd claif_gem
pip install -e .
```

### With CLAIF
```bash
# Install CLAIF with Gemini support
pip install claif claif_gem
```

### Prerequisites
You need to have the Gemini CLI binary installed and accessible. Set the path:
```bash
export GEMINI_CLI_PATH=/path/to/gemini-cli
```

## Command Line Usage

CLAIF_GEM provides its own Fire-based CLI with specialized features for Gemini:

### Basic Queries
```bash
# Ask Gemini a question
claif-gem query "Explain machine learning"

# Query with specific model
claif-gem query "Write a poem" --model gemini-pro

# Query with custom parameters
claif-gem query "Analyze this data" --temperature 0.5 --max-context 4000
```

### System Prompts
```bash
# Set system prompt for context
claif-gem query "Review this code" --system "You are a code reviewer"

# Complex system instructions
claif-gem query "Translate to French" --system "You are a professional translator"
```

### Auto-Approval Modes
```bash
# Auto-approve all actions (default)
claif-gem query "Make changes" --auto-approve

# Disable auto-approval for manual confirmation
claif-gem query "Delete files" --no-auto-approve

# Yes mode for all confirmations
claif-gem query "Update config" --yes-mode
```

### Streaming
```bash
# Stream responses in real-time
claif-gem stream "Tell me a story"

# Stream with specific model
claif-gem stream "Explain quantum physics" --model gemini-pro
```

### Model Management
```bash
# List available models
claif-gem models

# Show current configuration
claif-gem config show

# Set default model
claif-gem config set --default-model gemini-pro
```

### Health Check
```bash
# Check Gemini service health
claif-gem health

# Check with specific timeout
claif-gem health --timeout 30
```

## Python API Usage

### Basic Usage
```python
import asyncio
from claif_gem import query, GeminiOptions

async def main():
    # Simple query
    async for message in query("Hello, Gemini!"):
        print(message.content)
    
    # Query with options
    options = GeminiOptions(
        model="gemini-pro",
        temperature=0.7,
        system_prompt="You are a helpful assistant",
        auto_approve=True
    )
    async for message in query("Explain Python", options):
        print(message.content)

asyncio.run(main())
```

### Context Management
```python
from claif_gem.types import GeminiOptions

# Set maximum context length
options = GeminiOptions(
    max_context_length=8000,
    model="gemini-pro"
)

# Long conversation with context management
async for message in query("Let's discuss philosophy", options):
    print(message.content)
```

### Auto-Approval Control
```python
# Disable auto-approval for safety
options = GeminiOptions(
    auto_approve=False,
    yes_mode=False
)

# Query requiring manual confirmation
async for message in query("Modify system files", options):
    print(message.content)
```

### Subprocess Management
```python
from claif_gem.transport import GeminiTransport

# Create transport with custom settings
transport = GeminiTransport(
    cli_path="/usr/local/bin/gemini-cli",
    timeout=120
)

# Execute query
async for message in transport.query("Complex analysis", options):
    print(message.content)
```

## Why Use CLAIF_GEM?

### 1. **Google AI Integration**
- Access to Google's latest Gemini models
- High-quality language understanding and generation
- Multi-modal capabilities (when supported)

### 2. **Streamlined Workflow**
- Auto-approval mode for faster interactions
- Yes-mode for batch operations
- System prompt support for context setting

### 3. **Flexible Configuration**
- Customizable model selection
- Temperature and context control
- Timeout management for long operations

### 4. **Safety Features**
- Optional manual approval mode
- Timeout protection
- Error handling and recovery

## How It Works

### Architecture

```
┌─────────────────────┐
│    CLAIF Core       │
├─────────────────────┤
│   Gemini Provider   │
├─────────────────────┤
│    CLAIF_GEM        │
├─────────────────────┤
│  Subprocess Layer   │
├─────────────────────┤
│  Gemini CLI Binary  │
└─────────────────────┘
```

### Core Components

#### 1. **Main Module** (`__init__.py`)
Provides the main `query` function that:
- Converts CLAIF options to GeminiOptions
- Delegates to the client module
- Yields normalized messages

#### 2. **Client Module** (`client.py`)
- Manages the query lifecycle
- Handles option validation
- Coordinates with transport layer

#### 3. **Transport Module** (`transport.py`)
- `GeminiTransport`: Manages subprocess communication
- Handles CLI path resolution
- Implements timeout and error handling
- Parses CLI output into messages

#### 4. **Types Module** (`types.py`)
- `GeminiOptions`: Configuration for queries
- Type definitions for strong typing
- Default values and validation

#### 5. **CLI Module** (`cli.py`)
Fire-based CLI providing:
- Query and stream commands
- Configuration management
- Health checks
- Model listing

### Message Flow

1. Query enters through CLAIF interface
2. CLAIF_GEM converts options to GeminiOptions
3. Client validates and prepares the query
4. Transport spawns Gemini CLI subprocess
5. CLI arguments constructed from options
6. Subprocess output parsed into messages
7. Messages normalized to CLAIF format
8. Messages yielded to user

### Configuration

CLAIF_GEM inherits configuration from CLAIF and adds:

```toml
[providers.gemini]
enabled = true
cli_path = "/usr/local/bin/gemini-cli"
api_key_env = "GEMINI_API_KEY"
default_model = "gemini-pro"

[gemini.defaults]
auto_approve = true
yes_mode = true
max_context_length = 4000
temperature = 0.7

[gemini.safety]
timeout = 120
retry_on_error = true
```

### Environment Variables

- `GEMINI_CLI_PATH`: Path to Gemini CLI binary
- `GEMINI_API_KEY`: API key for Gemini
- `GEMINI_DEFAULT_MODEL`: Default model to use
- `GEMINI_AUTO_APPROVE`: Default auto-approval setting
- `GEMINI_TIMEOUT`: Default timeout in seconds

### CLI Arguments

The Gemini CLI is invoked with arguments based on options:

```bash
gemini-cli [model] \
  --auto-approve \
  --yes \
  --temperature 0.7 \
  --max-context-length 4000 \
  --system-prompt "..." \
  "prompt"
```

## Error Handling

CLAIF_GEM provides robust error handling:

```python
from claif_gem import query
from claif.common import ProviderError, TimeoutError

try:
    async for message in query("Generate content"):
        print(message.content)
except TimeoutError:
    print("Query timed out")
except ProviderError as e:
    print(f"Gemini error: {e}")
```

## Best Practices

1. **Use System Prompts**: Set context with system prompts for better results
2. **Manage Context Length**: Monitor context for long conversations
3. **Auto-Approval Caution**: Disable auto-approval for sensitive operations
4. **Model Selection**: Choose appropriate models for your use case
5. **Error Handling**: Implement proper error handling for production use

## Available Models

Common Gemini models include:
- `gemini-pro`: General-purpose model
- `gemini-pro-vision`: Multi-modal model
- `gemini-ultra`: Most capable model (when available)

Check current availability with:
```bash
claif-gem models
```

## Contributing

To contribute to CLAIF_GEM:

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/twardoch/claif_gem)
- [PyPI Package](https://pypi.org/project/claif_gem/)
- [CLAIF Framework](https://github.com/twardoch/claif)
- [Gemini Documentation](https://ai.google.dev/docs)