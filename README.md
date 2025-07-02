#`claif_gem` - Google Gemini Provider forClaif

## Quickstart

Claif_GEM provides a Python interface and CLI wrapper for Google's Gemini AI models. It integrates the Gemini CLI tool into the Claif framework, enabling you to query Gemini models with a simple command or Python API call. Version 1.0.4 improves subprocess reliability by switching to native asyncio.

```bash
pip install claif_gem && claif-gem query "Explain quantum computing in one sentence"
```

Claif_GEM is the Google Gemini provider implementation for the Claif (Command-Line Artificial Intelligence Framework). It wraps the [Gemini CLI](https://github.com/google-gemini/gemini-cli/) to integrate Google's Gemini AI models into the unifiedClaif ecosystem.

## What is`claif_gem`?

Claif_GEM provides a Python interface and command-line wrapper for the Google Gemini CLI tool. It enables seamless integration of Google's Gemini language models with the Claif framework through subprocess management and message translation.

Key features:
- **Subprocess-based integration** with the Gemini CLI binary
- **Automatic CLI discovery** across multiple platforms (Windows, macOS, Linux)
- **Fire-based CLI** with rich terminal output for direct usage
- **Async/await support** for efficient concurrent operations
- **Auto-approval and yes-mode** for streamlined workflows
- **Flexible configuration** via environment variables and options
- **Robust error handling** with timeout protection

## Installation

### Prerequisites

You need to have the Gemini CLI installed. Install it via npm:
```bash
npm install -g @google/gemini-cli
```

Or set the path to an existing installation:
```bash
export GEMINI_CLI_PATH=/path/to/gemini
```

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

### WithClaif Framework
```bash
# InstallClaif with all providers
pip install claif[all]

# Or just with Gemini support
pip install claif claif_gem
```

## CLI Usage

Claif_GEM provides a Fire-based CLI for direct interaction with Gemini:

### Basic Commands

```bash
# Simple query
claif-gem query "Explain quantum computing"

# Query with specific model
claif-gem query "Write a haiku" --model gemini-2.5-pro

# Query with parameters
claif-gem query "Analyze this code" --temperature 0.3 --max-context 8000

# With system prompt
claif-gem query "Translate to Spanish" --system "You are a professional translator"

# Stream responses
claif-gem stream "Tell me a story"

# Health check
claif-gem health

# List available models
claif-gem models

# Show configuration
claif-gem config show
```

### Options

- `--model`: Specify Gemini model (default: gemini-2.5-pro)
- `--temperature`: Control randomness (0-1)
- `--system`: Set system prompt for context
- `--auto-approve`: Auto-approve tool usage (default: true)
- `--yes-mode`: Automatically confirm all prompts (default: true)
- `--max-context`: Maximum context length
- `--timeout`: Query timeout in seconds
- `--show-metrics`: Display response metrics
- `--verbose`: Enable debug output

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
        model="gemini-2.5-pro",
        temperature=0.7,
        system_prompt="You are a helpful coding assistant",
        auto_approve=True,
        yes_mode=True
    )
    
    async for message in query("Explain Python decorators", options):
        print(message.content)

asyncio.run(main())
```

### Direct Client Usage

```python
from claif_gem.client import GeminiClient
from claif_gem.types import GeminiOptions

async def main():
    client = GeminiClient()
    options = GeminiOptions(
        model="gemini-2.5-pro",
        verbose=True
    )
    
    async for message in client.query("What is machine learning?", options):
        print(f"[{message.role}]: {message.content}")

asyncio.run(main())
```

### Transport Layer Access

```python
from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiOptions

async def main():
    transport = GeminiTransport()
    options = GeminiOptions(timeout=60)
    
    async for response in transport.send_query("Complex analysis", options):
        if hasattr(response, 'content'):
            print(response.content)

asyncio.run(main())
```

## How It Works

### Architecture Overview

```
┌─────────────────────┐
│   User Application  │
├─────────────────────┤
│   Claif Core       │
├─────────────────────┤
│   `claif_gem`        │
│  ┌───────────────┐  │
│  │   __init__.py │  │ ← Main entry point,Claif interface
│  ├───────────────┤  │
│  │    cli.py     │  │ ← Fire-based CLI commands
│  ├───────────────┤  │
│  │   client.py   │  │ ← Client orchestration
│  ├───────────────┤  │
│  │ transport.py  │  │ ← Subprocess management
│  ├───────────────┤  │
│  │   types.py    │  │ ← Type definitions
│  └───────────────┘  │
├─────────────────────┤
│  Subprocess Layer   │
├─────────────────────┤
│   Gemini CLI Binary │ ← External Node.js CLI
└─────────────────────┘
```

### Component Details

#### 1. **Main Module** (`__init__.py`)
- Provides the `query()` function as the main entry point
- ConvertsClaif's `ClaifOptions` to `GeminiOptions`
- Delegates to the client module for execution
- Exports public API: `query` and `GeminiOptions`

#### 2. **CLI Module** (`cli.py`)
- Fire-based command-line interface
- Commands: `query`, `stream`, `health`, `models`, `config`
- Rich console output with progress indicators
- Async execution with proper error handling
- Response formatting and metrics display

#### 3. **Client Module** (`client.py`)
- `GeminiClient` class manages the query lifecycle
- Coordinates with transport layer
- Converts Gemini messages toClaif message format
- Module-level `_client` instance for convenience

#### 4. **Transport Module** (`transport.py`)
- `GeminiTransport` handles subprocess communication
- CLI discovery across platforms (npm paths, common locations)
- Command-line argument construction from options
- Async subprocess execution with anyio
- Output parsing (JSON and plain text)
- Error handling and timeout management

#### 5. **Types Module** (`types.py`)
- `GeminiOptions`: Configuration dataclass
- `GeminiMessage`: Response message type
- `ResultMessage`: Metadata and error information
- Type conversion methods toClaif formats

### Message Flow

1. **Query Entry**: User calls `query()` with prompt and options
2. **Option Translation**:Claif options → GeminiOptions
3. **Client Processing**: GeminiClient validates and prepares query
4. **Transport Execution**:
   - Find Gemini CLI binary
   - Build command with arguments
   - Spawn subprocess with anyio
   - Read stdout/stderr streams
5. **Response Parsing**:
   - Try JSON parsing first
   - Fallback to plain text
   - Convert to GeminiMessage
6. **Message Conversion**: GeminiMessage →Claif Message
7. **Async Yield**: Messages yielded to caller

### CLI Discovery

The transport layer searches for the Gemini CLI in this order:
1. `GEMINI_CLI_PATH` environment variable
2. System PATH (`which gemini`)
3. Common installation paths:
   - `~/.local/bin/gemini`
   - `/usr/local/bin/gemini`
   - `/opt/gemini/bin/gemini`
4. NPM global paths:
   - Windows: `%APPDATA%/npm/gemini.cmd`
   - Unix: `~/.npm-global/bin/gemini`
   - System: `/usr/local/lib/node_modules/.bin/gemini`

### Command Construction

The Gemini CLI is invoked with arguments based on options:

```bash
gemini \
  -m <model> \
  -a  # auto-approve
  -y  # yes-mode
  -t <temperature> \
  -s <system-prompt> \
  --max-context <length> \
  -p "prompt"
```

### Environment Variables

- `GEMINI_CLI_PATH`: Path to Gemini CLI binary
- `GEMINI_SDK=1`: Set by transport to indicate SDK usage
- `Claif_PROVIDER=gemini`: Provider identification

## Why Use`claif_gem`?

1. **Unified Interface**: Access Gemini through the standardClaif API
2. **Cross-Platform**: Automatic CLI discovery works on Windows, macOS, Linux
3. **Async First**: Built on anyio for efficient concurrent operations
4. **Rich CLI**: Fire-based interface with progress indicators and formatting
5. **Type Safety**: Full type hints for better IDE support
6. **Error Handling**: Robust subprocess management with timeout protection
7. **Flexible Configuration**: Environment variables, options, and config files

## Development

### Project Structure
```
claif_gem/
├── src/claif_gem/
│   ├── __init__.py      # Main entry point
│   ├── cli.py           # Fire CLI implementation
│   ├── client.py        # Client orchestration
│   ├── transport.py     # Subprocess management
│   └── types.py         # Type definitions
├── tests/
│   └── test_package.py  # Basic tests
├── pyproject.toml       # Package configuration
└── README.md            # This file
```

### Running Tests
```bash
# Install development dependencies
pip install -e ".[dev,test]"

# Run tests
pytest

# Run with coverage
pytest --cov=claif_gem

# Run linting
ruff check src/claif_gem
ruff format src/claif_gem
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Links

- [GitHub Repository](https://github.com/twardoch/claif_gem)
- [PyPI Package](https://pypi.org/project/claif_gem/)
- [Claif Framework](https://github.com/twardoch/claif)
- [Gemini CLI](https://github.com/google-gemini/gemini-cli/)
- [Google AI Documentation](https://ai.google.dev/)