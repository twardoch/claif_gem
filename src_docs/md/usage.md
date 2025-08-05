# Usage Guide

Comprehensive guide to using `claif_gem` with detailed examples, patterns, and best practices. Master both the Python API and CLI interface.

## 🎯 Overview

`claif_gem` provides two main interfaces:

1. **Python API** - OpenAI-compatible client for programmatic use
2. **CLI Interface** - Command-line tool for direct interaction

Both interfaces share the same underlying capabilities and configuration options.

## 🐍 Python API Usage

### Basic Client Usage

The `GeminiClient` follows the exact same pattern as the OpenAI client:

```python
from claif_gem import GeminiClient

# Initialize client
client = GeminiClient()

# Basic completion
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "user", "content": "Explain Python decorators"}
    ]
)

print(response.choices[0].message.content)
```

### Message Formats

#### Single User Message

```python
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "user", "content": "What is machine learning?"}
    ]
)
```

#### System + User Messages

```python
response = client.chat.completions.create(
    model="gemini-1.5-pro",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to reverse a string"}
    ]
)
```

#### Multi-turn Conversation

```python
messages = [
    {"role": "system", "content": "You are a Python tutor."},
    {"role": "user", "content": "What are list comprehensions?"},
    {"role": "assistant", "content": "List comprehensions are a concise way to create lists in Python..."},
    {"role": "user", "content": "Can you show me an example?"}
]

response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=messages
)
```

### Streaming Responses

Stream responses for real-time output:

```python
def stream_response():
    client = GeminiClient()
    
    stream = client.chat.completions.create(
        model="gemini-1.5-pro",
        messages=[
            {"role": "user", "content": "Write a story about space exploration"}
        ],
        stream=True
    )
    
    print("Gemini: ", end="", flush=True)
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="", flush=True)
    print()  # New line at end

# Usage
stream_response()
```

### Parameter Control

#### Temperature and Creativity

```python
# Low temperature for factual/code responses
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[{"role": "user", "content": "Write a sorting algorithm"}],
    temperature=0.1  # More deterministic
)

# High temperature for creative responses
response = client.chat.completions.create(
    model="gemini-1.5-pro",
    messages=[{"role": "user", "content": "Write a creative poem"}],
    temperature=0.9  # More creative
)
```

#### Token Limits

```python
# Limit response length
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[{"role": "user", "content": "Summarize quantum computing"}],
    max_tokens=100  # Brief summary
)

# Longer responses
response = client.chat.completions.create(
    model="gemini-1.5-pro",
    messages=[{"role": "user", "content": "Detailed explanation of neural networks"}],
    max_tokens=2000  # Detailed explanation
)
```

### Model Selection Strategies

#### Task-Specific Model Selection

```python
class GeminiAssistant:
    def __init__(self):
        self.client = GeminiClient()
    
    def quick_answer(self, question: str) -> str:
        """For simple questions requiring fast responses."""
        response = self.client.chat.completions.create(
            model="gemini-1.5-flash",  # Fast model
            messages=[{"role": "user", "content": question}],
            temperature=0.3
        )
        return response.choices[0].message.content
    
    def detailed_analysis(self, topic: str) -> str:
        """For complex analysis requiring deep reasoning."""
        response = self.client.chat.completions.create(
            model="gemini-1.5-pro",  # Powerful model
            messages=[
                {"role": "system", "content": "Provide detailed, analytical responses."},
                {"role": "user", "content": f"Analyze: {topic}"}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        return response.choices[0].message.content
    
    def creative_writing(self, prompt: str) -> str:
        """For creative tasks."""
        response = self.client.chat.completions.create(
            model="gemini-1.5-pro",
            messages=[
                {"role": "system", "content": "You are a creative writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        return response.choices[0].message.content

# Usage
assistant = GeminiAssistant()
print(assistant.quick_answer("What is 2+2?"))
print(assistant.detailed_analysis("Impact of AI on education"))
print(assistant.creative_writing("Write a story about a time-traveling cat"))
```

### Error Handling

#### Robust Error Handling

```python
import time
from typing import Optional

def safe_chat_completion(
    client: GeminiClient,
    messages: list,
    model: str = "gemini-1.5-flash",
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> Optional[str]:
    """
    Make a chat completion with retry logic and error handling.
    """
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                timeout=60  # 60 second timeout
            )
            return response.choices[0].message.content
            
        except TimeoutError:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                
        except RuntimeError as e:
            if "quota" in str(e).lower():
                print("API quota exceeded. Waiting before retry...")
                time.sleep(retry_delay * 10)
            else:
                print(f"Runtime error: {e}")
                break
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            break
    
    return None

# Usage
client = GeminiClient()
result = safe_chat_completion(
    client,
    [{"role": "user", "content": "Hello!"}]
)

if result:
    print(result)
else:
    print("Failed to get response after retries")
```

### Batch Processing

#### Processing Multiple Queries

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

def process_queries_batch(queries: List[str], model: str = "gemini-1.5-flash") -> List[Tuple[str, str]]:
    """
    Process multiple queries in parallel.
    Returns list of (query, response) tuples.
    """
    client = GeminiClient()
    results = []
    
    def process_single_query(query: str) -> Tuple[str, str]:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": query}]
            )
            return (query, response.choices[0].message.content)
        except Exception as e:
            return (query, f"Error: {e}")
    
    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_query = {
            executor.submit(process_single_query, query): query 
            for query in queries
        }
        
        for future in as_completed(future_to_query):
            result = future.result()
            results.append(result)
    
    return results

# Usage
queries = [
    "What is Python?",
    "Explain machine learning",
    "How do neural networks work?",
    "What is cloud computing?",
    "Describe quantum computing"
]

results = process_queries_batch(queries)
for query, response in results:
    print(f"Q: {query}")
    print(f"A: {response[:100]}...\n")
```

### Advanced Patterns

#### Context-Aware Assistant

```python
class ContextAwareAssistant:
    def __init__(self, system_prompt: str = None):
        self.client = GeminiClient()
        self.conversation_history = []
        self.system_prompt = system_prompt or "You are a helpful assistant."
        
    def add_system_message(self):
        """Add system message if not already present."""
        if not self.conversation_history or self.conversation_history[0]["role"] != "system":
            self.conversation_history.insert(0, {
                "role": "system", 
                "content": self.system_prompt
            })
    
    def ask(self, question: str, stream: bool = False) -> str:
        """Ask a question with conversation context."""
        # Add user message
        self.conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Ensure system message is present
        self.add_system_message()
        
        try:
            if stream:
                return self._stream_response()
            else:
                return self._sync_response()
                
        except Exception as e:
            # Remove the failed user message
            self.conversation_history.pop()
            raise e
    
    def _sync_response(self) -> str:
        response = self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=self.conversation_history
        )
        
        answer = response.choices[0].message.content
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": answer
        })
        
        return answer
    
    def _stream_response(self) -> str:
        stream = self.client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=self.conversation_history,
            stream=True
        )
        
        full_response = ""
        print("Assistant: ", end="", flush=True)
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                print(content, end="", flush=True)
        
        print()  # New line
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        
        return full_response
    
    def clear_history(self):
        """Clear conversation history except system message."""
        self.conversation_history = []
        self.add_system_message()
    
    def get_context_size(self) -> int:
        """Get approximate token count of current context."""
        total_chars = sum(len(msg["content"]) for msg in self.conversation_history)
        return total_chars // 4  # Rough approximation: 4 chars per token

# Usage
assistant = ContextAwareAssistant("You are a Python programming expert.")

print(assistant.ask("What are Python decorators?"))
print("\n" + "="*50 + "\n")
print(assistant.ask("Can you show me an example?"))
print("\n" + "="*50 + "\n")
print(assistant.ask("How would I use this in a web framework?", stream=True))
```

#### File Processing Assistant

```python
import os
from pathlib import Path

class FileProcessingAssistant:
    def __init__(self):
        self.client = GeminiClient()
    
    def analyze_code_file(self, file_path: str) -> str:
        """Analyze a code file and provide insights."""
        path = Path(file_path)
        
        if not path.exists():
            return f"File not found: {file_path}"
        
        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"
        
        # Determine file type
        file_extension = path.suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.go': 'Go',
            '.rs': 'Rust'
        }
        
        language = language_map.get(file_extension, 'Unknown')
        
        prompt = f"""
        Analyze this {language} code file:
        
        File: {path.name}
        Language: {language}
        
        ```{language.lower()}
        {content}
        ```
        
        Please provide:
        1. Code summary
        2. Key functions/classes
        3. Potential improvements
        4. Code quality assessment
        """
        
        response = self.client.chat.completions.create(
            model="gemini-1.5-pro",  # Use Pro for code analysis
            messages=[
                {"role": "system", "content": "You are an expert code reviewer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Lower temperature for more consistent analysis
        )
        
        return response.choices[0].message.content
    
    def generate_documentation(self, file_path: str) -> str:
        """Generate documentation for a code file."""
        path = Path(file_path)
        
        if not path.exists():
            return f"File not found: {file_path}"
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file: {e}"
        
        prompt = f"""
        Generate comprehensive documentation for this code:
        
        File: {path.name}
        
        ```
        {content}
        ```
        
        Please provide:
        1. Module/file overview
        2. Function/class documentation
        3. Usage examples
        4. API reference
        
        Format the output in Markdown.
        """
        
        response = self.client.chat.completions.create(
            model="gemini-1.5-pro",
            messages=[
                {"role": "system", "content": "You are a technical documentation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content

# Usage
assistant = FileProcessingAssistant()

# Analyze a Python file
analysis = assistant.analyze_code_file("src/claif_gem/client.py")
print("Code Analysis:")
print(analysis)

# Generate documentation
docs = assistant.generate_documentation("src/claif_gem/client.py")
print("\nGenerated Documentation:")
print(docs)
```

## 💻 CLI Usage

### Basic CLI Commands

#### Simple Queries

```bash
# Basic query
claif-gem query "What is Python?"

# Query with specific model
claif-gem query "Explain machine learning" --model gemini-1.5-pro

# Query with temperature control
claif-gem query "Write a creative story" --temperature 0.9

# Limit response length
claif-gem query "Summarize quantum computing" --max-tokens 100
```

#### Interactive Chat Mode

```bash
# Start interactive chat
claif-gem chat

# Chat with specific model
claif-gem chat --model gemini-1.5-pro

# Chat with system prompt
claif-gem chat --system "You are a helpful coding assistant"

# Chat with custom temperature
claif-gem chat --temperature 0.7
```

#### System Prompts

```bash
# Professional translator
claif-gem query "Translate to Spanish: Hello, how are you?" \
  --system "You are a professional translator"

# Code reviewer
claif-gem query "Review this Python function: def add(a, b): return a + b" \
  --system "You are an expert code reviewer"

# Creative writer
claif-gem query "Write a story about a robot" \
  --system "You are a creative science fiction writer"
```

### Advanced CLI Usage

#### Streaming Responses

```bash
# Stream responses in real-time
claif-gem query "Write a detailed explanation of neural networks" --stream

# Stream with progress indicator
claif-gem query "Create a tutorial on REST APIs" --stream --verbose
```

#### Configuration Management

```bash
# Show current configuration
claif-gem config show

# Set default model
claif-gem config set default-model gemini-1.5-pro

# Set default temperature
claif-gem config set temperature 0.7

# Set timeout
claif-gem config set timeout 120

# Show all available models
claif-gem models

# Show detailed model information
claif-gem models --detailed
```

#### Output Formats

```bash
# JSON output
claif-gem query "Hello!" --json

# Raw output (no formatting)
claif-gem query "Hello!" --raw

# Show response metrics
claif-gem query "Hello!" --show-metrics

# Verbose output with debug info
claif-gem query "Hello!" --verbose
```

### CLI Scripting

#### Batch Processing Script

```bash
#!/bin/bash
# batch_process.sh - Process multiple queries

queries=(
    "What is Python?"
    "Explain machine learning"
    "How do neural networks work?"
    "What is cloud computing?"
)

echo "Processing ${#queries[@]} queries..."

for i in "${!queries[@]}"; do
    echo "Query $((i+1)): ${queries[i]}"
    claif-gem query "${queries[i]}" --model gemini-1.5-flash --max-tokens 100
    echo "---"
done

echo "Batch processing complete!"
```

#### File Processing Script

```bash
#!/bin/bash
# analyze_code.sh - Analyze code files

if [ $# -eq 0 ]; then
    echo "Usage: $0 <file1> [file2] [file3] ..."
    exit 1
fi

for file in "$@"; do
    if [ -f "$file" ]; then
        echo "Analyzing $file..."
        content=$(cat "$file")
        claif-gem query "Analyze this code and provide suggestions:\n\n$content" \
          --model gemini-1.5-pro \
          --system "You are an expert code reviewer"
        echo "---"
    else
        echo "File not found: $file"
    fi
done
```

#### Configuration Helper Script

```bash
#!/bin/bash
# setup_claif_gem.sh - Setup script for claif_gem

echo "Setting up claif_gem..."

# Check if API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "Please enter your Gemini API key:"
    read -s api_key
    export GEMINI_API_KEY="$api_key"
    echo "export GEMINI_API_KEY=\"$api_key\"" >> ~/.bashrc
fi

# Test installation
echo "Testing installation..."
if claif-gem query "Hello!" --show-metrics; then
    echo "✅ claif_gem is working correctly!"
else
    echo "❌ claif_gem setup failed"
    exit 1
fi

# Set default configuration
echo "Setting default configuration..."
claif-gem config set default-model gemini-1.5-flash
claif-gem config set temperature 0.7
claif-gem config set timeout 120

echo "Setup complete!"
```

## 🔧 Best Practices

### Performance Optimization

#### Model Selection Strategy

```python
class OptimizedGeminiClient:
    def __init__(self):
        self.client = GeminiClient()
        self.model_cache = {}
    
    def select_optimal_model(self, task_type: str, complexity: str) -> str:
        """Select the best model based on task requirements."""
        model_matrix = {
            ('simple', 'low'): 'gemini-1.5-flash-8b',
            ('simple', 'medium'): 'gemini-1.5-flash',
            ('simple', 'high'): 'gemini-1.5-flash',
            ('complex', 'low'): 'gemini-1.5-flash',
            ('complex', 'medium'): 'gemini-1.5-pro',
            ('complex', 'high'): 'gemini-1.5-pro',
            ('creative', 'low'): 'gemini-1.5-flash',
            ('creative', 'medium'): 'gemini-1.5-pro',
            ('creative', 'high'): 'gemini-1.5-pro',
        }
        
        return model_matrix.get((task_type, complexity), 'gemini-1.5-flash')
    
    def smart_completion(self, prompt: str, task_type: str = 'simple', complexity: str = 'medium'):
        """Make a completion with automatic model selection."""
        model = self.select_optimal_model(task_type, complexity)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content

# Usage
client = OptimizedGeminiClient()
print(client.smart_completion("What is 2+2?", "simple", "low"))
print(client.smart_completion("Analyze the economic impact of AI", "complex", "high"))
```

#### Caching Strategy

```python
import hashlib
import json
import time
from typing import Optional, Dict, Any

class CachedGeminiClient:
    def __init__(self, cache_ttl: int = 3600):  # 1 hour TTL
        self.client = GeminiClient()
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = cache_ttl
    
    def _generate_cache_key(self, messages: list, model: str, **kwargs) -> str:
        """Generate a cache key for the request."""
        cache_data = {
            'messages': messages,
            'model': model,
            **kwargs
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid."""
        return time.time() - cache_entry['timestamp'] < self.cache_ttl
    
    def cached_completion(self, messages: list, model: str = "gemini-1.5-flash", **kwargs) -> str:
        """Make a completion with caching."""
        cache_key = self._generate_cache_key(messages, model, **kwargs)
        
        # Check cache
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            print("Cache hit!")
            return self.cache[cache_key]['response']
        
        # Make API call
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        result = response.choices[0].message.content
        
        # Store in cache
        self.cache[cache_key] = {
            'response': result,
            'timestamp': time.time()
        }
        
        return result
    
    def clear_cache(self):
        """Clear the cache."""
        self.cache.clear()

# Usage
cached_client = CachedGeminiClient()

# First call - makes API request
result1 = cached_client.cached_completion([{"role": "user", "content": "What is Python?"}])

# Second call - uses cache
result2 = cached_client.cached_completion([{"role": "user", "content": "What is Python?"}])
```

### Security Best Practices

#### API Key Management

```python
import os
from pathlib import Path
import json

class SecureGeminiClient:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.client = GeminiClient(api_key=self.api_key)
    
    def _load_api_key(self) -> str:
        """Load API key from secure location."""
        # Priority order:
        # 1. Environment variable
        # 2. Config file
        # 3. Keyring (if available)
        
        # Try environment variable first
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return api_key
        
        # Try config file
        config_path = Path.home() / '.claif' / 'config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('providers', {}).get('gemini', {}).get('api_key')
            except Exception:
                pass
        
        # Try keyring (optional dependency)
        try:
            import keyring
            api_key = keyring.get_password('claif_gem', 'api_key')
            if api_key:
                return api_key
        except ImportError:
            pass
        
        raise ValueError(
            "API key not found. Set GEMINI_API_KEY environment variable "
            "or configure in ~/.claif/config.json"
        )
    
    def safe_completion(self, messages: list, **kwargs) -> str:
        """Make a completion with input sanitization."""
        # Sanitize messages
        sanitized_messages = []
        for msg in messages:
            # Remove potentially sensitive data patterns
            content = msg['content']
            
            # Remove API keys, passwords, etc.
            import re
            content = re.sub(r'[A-Za-z0-9]{32,}', '[REDACTED]', content)
            content = re.sub(r'password[:\s]*\S+', 'password: [REDACTED]', content, flags=re.IGNORECASE)
            
            sanitized_messages.append({
                'role': msg['role'],
                'content': content
            })
        
        return self.client.chat.completions.create(
            messages=sanitized_messages,
            **kwargs
        ).choices[0].message.content

# Usage
secure_client = SecureGeminiClient()
response = secure_client.safe_completion([
    {"role": "user", "content": "Help me debug this code"}
])
```

## 📊 Monitoring and Metrics

### Response Time Tracking

```python
import time
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class CompletionMetrics:
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration: float
    timestamp: float

class MetricsTracker:
    def __init__(self):
        self.client = GeminiClient()
        self.metrics: List[CompletionMetrics] = []
    
    def timed_completion(self, messages: list, model: str = "gemini-1.5-flash", **kwargs) -> tuple[str, CompletionMetrics]:
        """Make a completion and track metrics."""
        start_time = time.time()
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Create metrics
        metrics = CompletionMetrics(
            model=model,
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens,
            duration=duration,
            timestamp=start_time
        )
        
        self.metrics.append(metrics)
        
        return response.choices[0].message.content, metrics
    
    def get_average_response_time(self, model: str = None) -> float:
        """Get average response time for a model."""
        filtered_metrics = self.metrics
        if model:
            filtered_metrics = [m for m in self.metrics if m.model == model]
        
        if not filtered_metrics:
            return 0.0
        
        return sum(m.duration for m in filtered_metrics) / len(filtered_metrics)
    
    def get_token_stats(self) -> Dict[str, float]:
        """Get token usage statistics."""
        if not self.metrics:
            return {}
        
        total_prompt_tokens = sum(m.prompt_tokens for m in self.metrics)
        total_completion_tokens = sum(m.completion_tokens for m in self.metrics)
        
        return {
            'total_prompt_tokens': total_prompt_tokens,
            'total_completion_tokens': total_completion_tokens,
            'average_prompt_tokens': total_prompt_tokens / len(self.metrics),
            'average_completion_tokens': total_completion_tokens / len(self.metrics)
        }

# Usage
tracker = MetricsTracker()

response, metrics = tracker.timed_completion([
    {"role": "user", "content": "Explain quantum computing"}
])

print(f"Response time: {metrics.duration:.2f}s")
print(f"Tokens used: {metrics.total_tokens}")
print(f"Average response time: {tracker.get_average_response_time():.2f}s")
```

## ⏭️ Next Steps

Now that you understand the comprehensive usage patterns:

1. **[Configuration Guide](configuration.md)** - Learn about environment variables, config files, and customization
2. **[CLI Reference](cli-reference.md)** - Complete command-line interface documentation
3. **[API Reference](api-reference.md)** - Detailed Python API documentation
4. **[Architecture Guide](architecture.md)** - Understand the internal design

---

**Need more examples?** Check out our [GitHub discussions](https://github.com/twardoch/claif_gem/discussions) for community-contributed patterns and use cases.