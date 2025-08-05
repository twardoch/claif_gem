# API Reference

Complete Python API documentation for `claif_gem`. This reference covers all classes, methods, and functions with detailed examples and type information.

## 📖 Overview

The `claif_gem` package provides an OpenAI-compatible interface to Google Gemini models. The main components are:

- **GeminiClient** - Main client class with OpenAI-compatible API
- **Configuration** - Configuration management and settings
- **Types** - Type definitions and data classes
- **Exceptions** - Custom exceptions and error handling

## 🏗️ Module Structure

```
claif_gem/
├── __init__.py          # Main exports
├── client.py           # GeminiClient and OpenAI compatibility
├── cli.py              # Command-line interface
├── config.py           # Configuration management
├── types.py            # Type definitions
└── exceptions.py       # Custom exceptions
```

## 🚀 Main Client API

### GeminiClient

The primary interface for interacting with Gemini models using OpenAI-compatible patterns.

```python
from claif_gem import GeminiClient
```

#### Class Definition

```python
class GeminiClient:
    """OpenAI-compatible client for Google Gemini models."""
    
    def __init__(
        self,
        api_key: str | None = None,
        cli_path: str | None = None,
        timeout: float = 600.0,
        config: GeminiConfig | None = None
    ) -> None:
        """Initialize the Gemini client.
        
        Args:
            api_key: Google API key (defaults to GEMINI_API_KEY env var)
            cli_path: Path to gemini CLI executable (auto-detected if None)
            timeout: Command timeout in seconds
            config: Configuration object (overrides other parameters)
            
        Raises:
            FileNotFoundError: If Gemini CLI is not found
            ValueError: If API key is not provided or found
        """
```

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `api_key` | `str \| None` | Current API key |
| `timeout` | `float` | Default timeout in seconds |
| `chat` | `Chat` | Chat completions namespace |

#### Methods

##### `chat.completions.create()`

The main method for creating chat completions, fully compatible with OpenAI's interface.

```python
def create(
    self,
    *,
    messages: list[ChatCompletionMessageParam],
    model: str = "gemini-pro",
    frequency_penalty: float | None | NotGiven = NOT_GIVEN,
    function_call: Any | None | NotGiven = NOT_GIVEN,
    functions: list[Any] | None | NotGiven = NOT_GIVEN,
    logit_bias: dict[str, int] | None | NotGiven = NOT_GIVEN,
    logprobs: bool | None | NotGiven = NOT_GIVEN,
    max_tokens: int | None | NotGiven = NOT_GIVEN,
    n: int | None | NotGiven = NOT_GIVEN,
    presence_penalty: float | None | NotGiven = NOT_GIVEN,
    response_format: Any | None | NotGiven = NOT_GIVEN,
    seed: int | None | NotGiven = NOT_GIVEN,
    stop: str | None | list[str] | NotGiven = NOT_GIVEN,
    stream: bool | None | NotGiven = NOT_GIVEN,
    temperature: float | None | NotGiven = NOT_GIVEN,
    tool_choice: Any | None | NotGiven = NOT_GIVEN,
    tools: list[Any] | None | NotGiven = NOT_GIVEN,
    top_logprobs: int | None | NotGiven = NOT_GIVEN,
    top_p: float | None | NotGiven = NOT_GIVEN,
    user: str | NotGiven = NOT_GIVEN,
    extra_headers: Any | None | NotGiven = NOT_GIVEN,
    extra_query: Any | None | NotGiven = NOT_GIVEN,
    extra_body: Any | None | NotGiven = NOT_GIVEN,
    timeout: float | NotGiven = NOT_GIVEN,
) -> ChatCompletion | Iterator[ChatCompletionChunk]:
    """Create a chat completion using Gemini CLI.
    
    Args:
        messages: List of conversation messages
        model: Model name to use
        temperature: Sampling temperature (0.0-2.0)
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response
        timeout: Request timeout in seconds
        
    Returns:
        ChatCompletion object or Iterator of ChatCompletionChunk for streaming
        
    Raises:
        TimeoutError: If request times out
        RuntimeError: If CLI execution fails
        ValueError: If parameters are invalid
    """
```

#### Examples

##### Basic Usage

```python
from claif_gem import GeminiClient

# Initialize client
client = GeminiClient()

# Simple completion
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

##### Advanced Usage

```python
from claif_gem import GeminiClient

client = GeminiClient(timeout=300)

# Complex conversation with system prompt
response = client.chat.completions.create(
    model="gemini-1.5-pro",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to calculate fibonacci numbers"}
    ],
    temperature=0.3,
    max_tokens=500
)

print(response.choices[0].message.content)
print(f"Usage: {response.usage}")
```

##### Streaming

```python
from claif_gem import GeminiClient

client = GeminiClient()

# Stream response
stream = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "user", "content": "Tell me a story"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

##### Error Handling

```python
from claif_gem import GeminiClient
from claif_gem.exceptions import GeminiError, TimeoutError

client = GeminiClient()

try:
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "Hello!"}],
        timeout=30
    )
    print(response.choices[0].message.content)
    
except TimeoutError:
    print("Request timed out")
except GeminiError as e:
    print(f"Gemini API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## 🔧 Configuration API

### GeminiConfig

Configuration management for claif_gem settings.

```python
from claif_gem.config import GeminiConfig
```

#### Class Definition

```python
@dataclass
class GeminiConfig:
    """Configuration settings for GeminiClient."""
    
    # Authentication
    api_key: str | None = None
    
    # Model settings
    default_model: str = "gemini-1.5-flash"
    temperature: float = 0.7
    max_tokens: int | None = None
    
    # CLI settings
    cli_path: str | None = None
    timeout: int = 120
    auto_approve: bool = True
    yes_mode: bool = True
    
    # Behavior settings
    verbose: bool = False
    stream: bool = False
    
    # Advanced settings
    retry_attempts: int = 3
    retry_delay: float = 1.0
```

#### Methods

##### `from_dict()`

```python
@classmethod
def from_dict(cls, config_dict: dict) -> 'GeminiConfig':
    """Create configuration from dictionary.
    
    Args:
        config_dict: Dictionary containing configuration values
        
    Returns:
        GeminiConfig instance
        
    Example:
        config = GeminiConfig.from_dict({
            'default_model': 'gemini-1.5-pro',
            'temperature': 0.5
        })
    """
```

##### `from_file()`

```python
@classmethod
def from_file(cls, file_path: str) -> 'GeminiConfig':
    """Load configuration from JSON file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        GeminiConfig instance
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        config = GeminiConfig.from_file('~/.claif/config.json')
    """
```

##### `to_dict()`

```python
def to_dict(self) -> dict:
    """Convert configuration to dictionary.
    
    Returns:
        Dictionary representation of configuration
        
    Example:
        config_dict = config.to_dict()
    """
```

##### `save_to_file()`

```python
def save_to_file(self, file_path: str) -> None:
    """Save configuration to JSON file.
    
    Args:
        file_path: Path where to save the configuration
        
    Example:
        config.save_to_file('~/.claif/config.json')
    """
```

#### Examples

```python
from claif_gem.config import GeminiConfig

# Create configuration with custom settings
config = GeminiConfig(
    default_model="gemini-1.5-pro",
    temperature=0.5,
    timeout=300,
    verbose=True
)

# Save to file
config.save_to_file("my_config.json")

# Load from file
loaded_config = GeminiConfig.from_file("my_config.json")

# Use with client
from claif_gem import GeminiClient
client = GeminiClient(config=config)
```

## 📊 Type Definitions

### Message Types

Compatible with OpenAI's message format:

```python
from openai.types.chat import ChatCompletionMessageParam

# Supported message types
ChatCompletionMessageParam = Union[
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionFunctionMessageParam,
]
```

### Response Types

#### ChatCompletion

```python
from openai.types.chat import ChatCompletion

class ChatCompletion:
    """Chat completion response object."""
    
    id: str                           # Unique identifier
    object: str                       # Object type ("chat.completion")
    created: int                      # Unix timestamp
    model: str                        # Model used
    choices: list[Choice]             # Response choices
    usage: CompletionUsage           # Token usage information
```

#### ChatCompletionChunk

```python
from openai.types.chat import ChatCompletionChunk

class ChatCompletionChunk:
    """Streaming chat completion chunk."""
    
    id: str                           # Unique identifier
    object: str                       # Object type ("chat.completion.chunk")
    created: int                      # Unix timestamp
    model: str                        # Model used
    choices: list[ChunkChoice]        # Response choices
```

#### Choice

```python
from openai.types.chat.chat_completion import Choice

class Choice:
    """Individual completion choice."""
    
    index: int                        # Choice index
    message: ChatCompletionMessage    # The completion message
    finish_reason: str | None         # Reason for completion end
    logprobs: dict | None            # Log probabilities
```

#### CompletionUsage

```python
from openai.types import CompletionUsage

class CompletionUsage:
    """Token usage information."""
    
    prompt_tokens: int                # Tokens in prompt
    completion_tokens: int            # Tokens in completion
    total_tokens: int                 # Total tokens used
```

### Custom Types

#### GeminiMessage

```python
from claif_gem.types import GeminiMessage

@dataclass
class GeminiMessage:
    """Internal message representation."""
    
    role: str                         # Message role (system, user, assistant)
    content: str                      # Message content
    metadata: dict[str, Any] | None = None  # Additional metadata
    
    def to_claif_message(self) -> Message:
        """Convert to Claif framework message format."""
```

#### GeminiOptions

```python
from claif_gem.types import GeminiOptions

@dataclass
class GeminiOptions:
    """Options for Gemini API calls."""
    
    model: str | None = None          # Model to use
    temperature: float | None = None  # Sampling temperature
    max_tokens: int | None = None     # Maximum tokens
    system_prompt: str | None = None  # System prompt
    auto_approve: bool = True         # Auto-approve CLI operations
    yes_mode: bool = True             # Yes mode for prompts
    timeout: int | None = None        # Request timeout
    verbose: bool = False             # Enable verbose output
```

## ⚠️ Exception Handling

### Exception Hierarchy

```python
from claif_gem.exceptions import (
    GeminiError,
    GeminiTimeoutError,
    GeminiAPIError,
    GeminiCLIError,
    GeminiConfigError
)

# Exception hierarchy:
# GeminiError (base)
# ├── GeminiTimeoutError
# ├── GeminiAPIError
# ├── GeminiCLIError
# └── GeminiConfigError
```

### Exception Classes

#### GeminiError

Base exception for all claif_gem errors.

```python
class GeminiError(Exception):
    """Base exception for Gemini-related errors."""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
```

#### GeminiTimeoutError

Raised when operations timeout.

```python
class GeminiTimeoutError(GeminiError):
    """Raised when Gemini operations timeout."""
    
    def __init__(self, timeout: float, operation: str = "request"):
        message = f"{operation.capitalize()} timed out after {timeout} seconds"
        super().__init__(message, {"timeout": timeout, "operation": operation})
```

#### GeminiAPIError

Raised for API-related errors.

```python
class GeminiAPIError(GeminiError):
    """Raised for Gemini API errors."""
    
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message, {"status_code": status_code})
        self.status_code = status_code
```

#### GeminiCLIError

Raised for CLI execution errors.

```python
class GeminiCLIError(GeminiError):
    """Raised when Gemini CLI execution fails."""
    
    def __init__(self, message: str, return_code: int, stderr: str = ""):
        details = {"return_code": return_code, "stderr": stderr}
        super().__init__(message, details)
        self.return_code = return_code
        self.stderr = stderr
```

#### GeminiConfigError

Raised for configuration errors.

```python
class GeminiConfigError(GeminiError):
    """Raised for configuration-related errors."""
    
    def __init__(self, message: str, config_key: str | None = None):
        super().__init__(message, {"config_key": config_key})
        self.config_key = config_key
```

### Error Handling Examples

#### Basic Error Handling

```python
from claif_gem import GeminiClient
from claif_gem.exceptions import GeminiError, GeminiTimeoutError

client = GeminiClient()

try:
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
    
except GeminiTimeoutError as e:
    print(f"Request timed out: {e.details['timeout']} seconds")
    
except GeminiError as e:
    print(f"Gemini error: {e.message}")
    if e.details:
        print(f"Details: {e.details}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

#### Advanced Error Handling with Retry

```python
import time
from claif_gem import GeminiClient
from claif_gem.exceptions import GeminiError, GeminiTimeoutError, GeminiAPIError

def robust_completion(client: GeminiClient, messages: list, max_retries: int = 3):
    """Make a completion with retry logic."""
    
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=messages,
                timeout=60
            )
            
        except GeminiTimeoutError:
            if attempt < max_retries - 1:
                print(f"Timeout on attempt {attempt + 1}, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
            
        except GeminiAPIError as e:
            if e.status_code == 429:  # Rate limit
                if attempt < max_retries - 1:
                    print(f"Rate limited, waiting before retry...")
                    time.sleep(5)
                    continue
            raise
            
        except GeminiError as e:
            print(f"Gemini error on attempt {attempt + 1}: {e.message}")
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise
    
    raise GeminiError("Max retries exceeded")

# Usage
client = GeminiClient()
try:
    response = robust_completion(client, [
        {"role": "user", "content": "Hello!"}
    ])
    print(response.choices[0].message.content)
except GeminiError as e:
    print(f"Failed after retries: {e}")
```

## 🔌 Utility Functions

### Model Name Mapping

```python
def map_model_name(model: str) -> str:
    """Map OpenAI-style model names to Gemini equivalents.
    
    Args:
        model: Model name (OpenAI or Gemini format)
        
    Returns:
        Gemini model name
        
    Example:
        >>> map_model_name("gpt-4")
        "gemini-1.5-pro"
        >>> map_model_name("gemini-1.5-flash")
        "gemini-1.5-flash"
    """
```

### CLI Path Discovery

```python
def find_gemini_cli(cli_path: str | None = None) -> str:
    """Find the Gemini CLI executable.
    
    Args:
        cli_path: Optional custom path to search first
        
    Returns:
        Path to Gemini CLI executable
        
    Raises:
        FileNotFoundError: If CLI is not found
        
    Example:
        >>> find_gemini_cli()
        "/usr/local/bin/gemini"
    """
```

### Response Parsing

```python
def parse_gemini_response(output: str) -> str:
    """Parse Gemini CLI output into clean response text.
    
    Args:
        output: Raw CLI output
        
    Returns:
        Cleaned response content
        
    Example:
        >>> parse_gemini_response('{"candidates": [{"content": {"parts": [{"text": "Hello!"}]}}]}')
        "Hello!"
    """
```

## 📚 Usage Patterns

### Factory Pattern for Multiple Clients

```python
from claif_gem import GeminiClient
from claif_gem.config import GeminiConfig

class GeminiClientFactory:
    """Factory for creating configured GeminiClient instances."""
    
    @staticmethod
    def create_development_client() -> GeminiClient:
        """Create client optimized for development."""
        config = GeminiConfig(
            default_model="gemini-1.5-flash",
            temperature=0.7,
            timeout=300,
            verbose=True
        )
        return GeminiClient(config=config)
    
    @staticmethod
    def create_production_client() -> GeminiClient:
        """Create client optimized for production."""
        config = GeminiConfig(
            default_model="gemini-1.5-pro",
            temperature=0.3,
            timeout=120,
            verbose=False,
            retry_attempts=5
        )
        return GeminiClient(config=config)
    
    @staticmethod
    def create_creative_client() -> GeminiClient:
        """Create client optimized for creative tasks."""
        config = GeminiConfig(
            default_model="gemini-1.5-pro",
            temperature=0.9,
            timeout=180
        )
        return GeminiClient(config=config)

# Usage
dev_client = GeminiClientFactory.create_development_client()
prod_client = GeminiClientFactory.create_production_client()
creative_client = GeminiClientFactory.create_creative_client()
```

### Context Manager for Resource Management

```python
from contextlib import contextmanager
from claif_gem import GeminiClient

@contextmanager
def gemini_session(config=None):
    """Context manager for Gemini client sessions."""
    client = GeminiClient(config=config)
    try:
        yield client
    finally:
        # Cleanup if needed
        pass

# Usage
with gemini_session() as client:
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.choices[0].message.content)
```

### Async Wrapper (Future Enhancement)

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from claif_gem import GeminiClient

class AsyncGeminiClient:
    """Async wrapper for GeminiClient."""
    
    def __init__(self, *args, **kwargs):
        self.client = GeminiClient(*args, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def create_completion(self, **kwargs):
        """Async completion creation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            lambda: self.client.chat.completions.create(**kwargs)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.executor.shutdown(wait=True)

# Usage
async def main():
    async with AsyncGeminiClient() as client:
        response = await client.create_completion(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(response.choices[0].message.content)

# asyncio.run(main())
```

## ⏭️ Next Steps

Now that you understand the complete API:

1. **[Architecture Guide](architecture.md)** - Learn how claif_gem works internally
2. **[Testing Guide](testing.md)** - Understand testing strategies and setup
3. **[Contributing Guide](contributing.md)** - Contribute to the project
4. **[Usage Guide](usage.md)** - See practical examples and patterns

---

**API Questions?** Check our [discussions](https://github.com/twardoch/claif_gem/discussions) or [open an issue](https://github.com/twardoch/claif_gem/issues).