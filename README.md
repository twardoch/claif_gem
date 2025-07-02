# claif_gem - Gemini Provider for Claif

## Quickstart

```bash
# Install and start using Gemini
pip install claif_gem
claif-gem query "Explain quantum computing in simple terms"

# Or use it with the Claif framework
pip install claif[all]
claif query "Write a haiku about Python" --provider gemini

# Stream responses with live display
claif-gem stream "Tell me a story about AI"

# Use auto-approve mode for faster responses
claif-gem query "Analyze this code" --auto-approve --yes-mode
```

## What is claif_gem?

`claif_gem` is the Google Gemini provider for the Claif framework. It wraps the [Gemini CLI](https://github.com/google-gemini/gemini-cli/) tool to integrate Google's powerful Gemini language models into the unified Claif ecosystem through subprocess management and clean message translation.

**Key Features:**
- **Subprocess-based integration** - Reliable communication with Gemini CLI
- **Auto-approve & yes-mode** - Streamlined workflows without interruptions
- **Cross-platform CLI discovery** - Works on Windows, macOS, and Linux
- **Async/await throughout** - Built on anyio for efficiency
- **Rich CLI interface** - Beautiful terminal output with Fire
- **Type-safe API** - Comprehensive type hints for IDE support
- **Robust error handling** - Timeout protection and graceful failures

## Installation

### Prerequisites

Install the Gemini CLI via npm:

```bash
npm install -g @google/gemini-cli
```

Or set the path to an existing installation:

```bash
export GEMINI_CLI_PATH=/path/to/gemini
```

### Basic Installation

```bash
# Core package only
pip install claif_gem

# With Claif framework
pip install claif claif_gem

# All Claif providers
pip install claif[all]
```

### Installing Gemini CLI with Claif

```bash
# Using Claif's installer (recommended)
pip install claif && claif install gemini

# Or using claif_gem's installer
python -m claif_gem.install

# Manual installation with bun (faster)
bun add -g @google/gemini-cli
```

### Development Installation

```bash
git clone https://github.com/twardoch/claif_gem.git
cd claif_gem
pip install -e ".[dev,test]"
```

## CLI Usage

`claif_gem` provides a Fire-based CLI for direct interaction with Gemini.

### Basic Commands

```bash
# Simple query
claif-gem query "Explain machine learning"

# Query with specific model
claif-gem query "Write Python code for binary search" --model gemini-2.5-pro

# Set parameters
claif-gem query "Analyze this data" --temperature 0.3 --max-context 8000

# With system prompt
claif-gem query "Translate to French" --system "You are a professional translator"

# Stream responses
claif-gem stream "Create a detailed tutorial on REST APIs"

# Health check
claif-gem health

# List models
claif-gem models

# Show configuration
claif-gem config show
```

### Advanced Options

```bash
# Control tool approval
claif-gem query "Process these files" --auto-approve  # Auto-approve tool use
claif-gem query "Analyze code" --no-auto-approve      # Manual approval

# Yes mode for all prompts
claif-gem query "Refactor this module" --yes-mode

# Verbose output for debugging
claif-gem query "Debug this error" --verbose

# Custom timeout
claif-gem query "Complex analysis" --timeout 300

# Show response metrics
claif-gem query "Quick question" --show-metrics
```

### Configuration Management

```bash
# Show current config
claif-gem config show

# Set values
claif-gem config set --default-model gemini-2.5-pro
claif-gem config set --auto-approve true
claif-gem config set --timeout 180

# Save configuration
claif-gem config save
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

async def use_client():
    client = GeminiClient()
    
    options = GeminiOptions(
        model="gemini-2.5-pro",
        verbose=True,
        max_context_length=16000
    )
    
    async for message in client.query("What is machine learning?", options):
        print(f"[{message.role}]: {message.content}")

asyncio.run(use_client())
```

### Transport Layer Access

```python
from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiOptions

async def direct_transport():
    transport = GeminiTransport()
    
    options = GeminiOptions(
        timeout=120,
        auto_approve=True
    )
    
    async for response in transport.send_query("Explain async programming", options):
        if hasattr(response, 'content'):
            print(response.content)

asyncio.run(direct_transport())
```

### Error Handling

```python
from claif.common import ProviderError, TransportError
from claif_gem import query, GeminiOptions

async def safe_query():
    try:
        options = GeminiOptions(timeout=60)
        async for message in query("Complex task", options):
            print(message.content)
            
    except TransportError as e:
        print(f"Transport error: {e}")
        # Retry with different settings
        
    except ProviderError as e:
        print(f"Gemini error: {e}")
        
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(safe_query())
```

### Using with Claif Framework

```python
from claif import query as claif_query, Provider, ClaifOptions

async def use_with_claif():
    options = ClaifOptions(
        provider=Provider.GEMINI,
        model="gemini-2.5-pro",
        temperature=0.5,
        system_prompt="You are a data science expert"
    )
    
    async for message in claif_query("Explain neural networks", options):
        print(message.content)

asyncio.run(use_with_claif())
```

## How It Works

### Architecture Overview

```
┌─────────────────────┐
│   User Application  │
├─────────────────────┤
│   Claif Core       │
├─────────────────────┤
│   claif_gem        │
│  ┌───────────────┐  │
│  │   __init__.py │  │ ← Main entry point, Claif interface
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

### Core Components

#### Main Module (`__init__.py`)

Entry point providing the `query()` function:

```python
async def query(
    prompt: str,
    options: ClaifOptions | None = None
) -> AsyncIterator[Message]:
    """Query Gemini with Claif-compatible interface."""
    # Convert options
    gemini_options = _convert_options(options) if options else GeminiOptions()
    
    # Delegate to client
    async for message in _client.query(prompt, gemini_options):
        yield message
```

Features:
- Thin wrapper design
- Option conversion between Claif and Gemini formats
- Module-level client instance
- Clean async generator interface

#### CLI Module (`cli.py`)

Fire-based command-line interface:

```python
class GeminiCLI:
    def query(self, prompt: str, **kwargs):
        """Execute a query to Gemini."""
        
    def stream(self, prompt: str, **kwargs):
        """Stream responses in real-time."""
        
    def health(self):
        """Check Gemini CLI availability."""
        
    def config(self, action: str = "show", **kwargs):
        """Manage configuration."""
```

Features:
- Rich console output with progress indicators
- Response formatting and metrics
- Async execution with error handling
- Configuration persistence

#### Client Module (`client.py`)

Manages the query lifecycle:

```python
class GeminiClient:
    def __init__(self):
        self.transport = GeminiTransport()
        
    async def query(self, prompt: str, options: GeminiOptions):
        # Send query via transport
        async for gemini_msg in self.transport.send_query(prompt, options):
            # Convert to Claif format
            yield self._convert_message(gemini_msg)
```

Features:
- Transport lifecycle management
- Message format conversion
- Error propagation
- Clean separation of concerns

#### Transport Module (`transport.py`)

Handles subprocess communication:

```python
class GeminiTransport:
    async def send_query(self, prompt: str, options: GeminiOptions):
        # Find CLI
        cli_path = self._find_cli_path()
        
        # Build command
        cmd = self._build_command(cli_path, prompt, options)
        
        # Execute and stream
        async with await anyio.open_process(cmd) as proc:
            async for line in proc.stdout:
                yield self._parse_line(line)
```

Key methods:
- `_find_cli_path()` - Multi-location CLI discovery
- `_build_command()` - Safe argument construction
- `_parse_output_line()` - JSON and plain text parsing
- Timeout management with process cleanup

#### Types Module (`types.py`)

Type definitions and conversions:

```python
@dataclass
class GeminiOptions:
    model: str | None = None
    temperature: float | None = None
    system_prompt: str | None = None
    auto_approve: bool = True
    yes_mode: bool = True
    max_context_length: int | None = None
    timeout: int | None = None
    verbose: bool = False

@dataclass
class GeminiMessage:
    role: str
    content: str
    metadata: dict[str, Any] | None = None
    
    def to_claif_message(self) -> Message:
        """Convert to Claif format."""
```

### Message Flow

1. **User Input** → CLI command or API call
2. **Option Translation** → ClaifOptions → GeminiOptions
3. **Client Processing** → GeminiClient prepares query
4. **Transport Execution**:
   - Find Gemini CLI binary
   - Build command with arguments
   - Spawn subprocess with anyio
   - Read stdout/stderr streams
5. **Response Parsing**:
   - Try JSON parsing first
   - Fallback to plain text
   - Convert to GeminiMessage
6. **Message Conversion** → GeminiMessage → Claif Message
7. **Async Yield** → Messages yielded to caller

### CLI Discovery

The transport searches for Gemini CLI in this order:

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
  -a          # auto-approve
  -y          # yes-mode
  -t <temp>   # temperature
  -s <prompt> # system prompt
  --max-context <length> \
  -p "user prompt"
```

### Code Structure

```
claif_gem/
├── src/claif_gem/
│   ├── __init__.py      # Main entry point
│   ├── cli.py           # Fire CLI implementation
│   ├── client.py        # Client orchestration
│   ├── transport.py     # Subprocess management
│   ├── types.py         # Type definitions
│   └── install.py       # CLI installation helper
├── tests/
│   └── test_package.py  # Basic tests
├── pyproject.toml       # Package configuration
├── README.md            # This file
└── CLAUDE.md            # Development guide
```

### Configuration

Environment variables:
- `GEMINI_CLI_PATH` - Path to Gemini CLI binary
- `GEMINI_SDK=1` - Set by transport to indicate SDK usage
- `CLAIF_PROVIDER=gemini` - Provider identification

Config file (`~/.claif/config.json`):
```json
{
    "providers": {
        "gemini": {
            "model": "gemini-2.5-pro",
            "auto_approve": true,
            "yes_mode": true,
            "max_context_length": 32000,
            "timeout": 180
        }
    }
}
```

## Installation with Bun

For faster installation, use Bun:

```bash
# Install bun
curl -fsSL https://bun.sh/install | bash

# Install Gemini CLI
bun add -g @google/gemini-cli

# Or use Claif's bundled installer
pip install claif
claif install gemini  # Uses bun internally
```

Benefits of Bun:
- 10x faster npm installs
- Creates standalone executables
- No Node.js version conflicts
- Cross-platform compatibility

## Why Use claif_gem?

### 1. **Unified Interface**
- Access Gemini through standard Claif API
- Switch between providers with one parameter
- Consistent error handling across providers

### 2. **Cross-Platform**
- Automatic CLI discovery on all platforms
- Platform-specific path handling
- Works in diverse environments

### 3. **Developer Experience**
- Full type hints for IDE support
- Rich CLI with progress indicators
- Clean async/await patterns
- Comprehensive error messages

### 4. **Production Ready**
- Robust subprocess management
- Timeout protection
- Graceful error recovery
- Extensive logging

### 5. **Flexible Configuration**
- Environment variables
- Config files
- CLI arguments
- Sensible defaults

## Best Practices

1. **Use auto-approve for trusted operations** - Speeds up workflows
2. **Set appropriate timeouts** - Prevent hanging on complex queries
3. **Enable verbose mode for debugging** - See full subprocess communication
4. **Use system prompts** - Set context for better responses
5. **Configure max context length** - Based on your use case
6. **Handle errors gracefully** - Implement retry logic
7. **Use streaming for long responses** - Better user experience

## Contributing

See [CLAUDE.md](CLAUDE.md) for development guidelines.

### Development Setup

```bash
# Clone repository
git clone https://github.com/twardoch/claif_gem.git
cd claif_gem

# Install with dev dependencies
pip install -e ".[dev,test]"

# Run tests
pytest

# Format code
ruff format src/claif_gem tests

# Lint
ruff check src/claif_gem tests

# Type check
mypy src/claif_gem
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claif_gem --cov-report=html

# Run specific test
pytest tests/test_transport.py -v

# Test CLI commands
python -m claif_gem.cli health
python -m claif_gem.cli models
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Adam Twardoch

## Links

### claif_gem Resources

- [GitHub Repository](https://github.com/twardoch/claif_gem) - Source code
- [PyPI Package](https://pypi.org/project/claif_gem/) - Latest release
- [Issue Tracker](https://github.com/twardoch/claif_gem/issues) - Bug reports
- [Discussions](https://github.com/twardoch/claif_gem/discussions) - Q&A

### Related Projects

**Claif Ecosystem:**
- [Claif](https://github.com/twardoch/claif) - Main framework
- [claif_cla](https://github.com/twardoch/claif_cla) - Claude provider
- [claif_cod](https://github.com/twardoch/claif_cod) - Codex provider

**Upstream Projects:**
- [Gemini CLI](https://github.com/google-gemini/gemini-cli/) - Google's CLI
- [Google AI Studio](https://ai.google.dev/) - Gemini documentation
- [Google AI Python SDK](https://github.com/google/generative-ai-python) - Python SDK

**Tools & Libraries:**
- [Fire](https://github.com/google/python-fire) - CLI framework
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [anyio](https://github.com/agronholm/anyio) - Async compatibility
- [Bun](https://bun.sh) - Fast JavaScript runtime