# Quick Start Guide

Get up and running with `claif_gem` in just 5 minutes! This guide covers the essential steps to start using Google Gemini through the OpenAI-compatible API.

## 🚀 Prerequisites

Before you begin, ensure you have:

- **Python 3.12+** installed
- **Node.js 18+** or **Bun** for Gemini CLI installation
- A **Google API key** for Gemini access

!!! tip "Get Your API Key"
    Get your free Google API key from [Google AI Studio](https://ai.google.dev/). No credit card required for the free tier!

## ⚡ 1-Minute Setup

### Step 1: Install claif_gem

=== "Standard Installation"

    ```bash
    pip install claif_gem
    ```

=== "With Development Tools"

    ```bash
    pip install "claif_gem[dev,test]"
    ```

=== "Full Claif Ecosystem"

    ```bash
    pip install "claif[all]"  # Includes all providers
    ```

### Step 2: Install Gemini CLI

=== "Using npm (Standard)"

    ```bash
    npm install -g @google/gemini-cli
    ```

=== "Using Bun (Faster)"

    ```bash
    # Install Bun first
    curl -fsSL https://bun.sh/install | bash
    
    # Install Gemini CLI with Bun
    bun add -g @google/gemini-cli
    ```

=== "Auto-Install Helper"

    ```bash
    # Let claif_gem install it for you
    python -c "import claif_gem.install; claif_gem.install.install_gemini_cli()"
    ```

### Step 3: Set Your API Key

=== "Environment Variable (Recommended)"

    ```bash
    export GEMINI_API_KEY="your-api-key-here"
    ```

=== "In Code"

    ```python
    from claif_gem import GeminiClient
    
    client = GeminiClient(api_key="your-api-key-here")
    ```

=== "Configuration File"

    Create `~/.claif/config.json`:
    ```json
    {
      "providers": {
        "gemini": {
          "api_key": "your-api-key-here"
        }
      }
    }
    ```

## 🎯 First Usage

### Basic Query (OpenAI-Style)

```python
from claif_gem import GeminiClient

# Initialize client
client = GeminiClient()

# Create a chat completion - exactly like OpenAI!
response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "user", "content": "Explain Python decorators in simple terms"}
    ]
)

# Access the response
print(response.choices[0].message.content)
```

**Expected Output:**
```
Python decorators are like gift wrappers for functions. They take a function, 
add extra functionality to it (like logging or timing), and return the enhanced 
function. You apply them using the @ symbol above a function definition...
```

### Streaming Response

```python
from claif_gem import GeminiClient

client = GeminiClient()

# Stream responses for real-time output
stream = client.chat.completions.create(
    model="gemini-1.5-pro",
    messages=[
        {"role": "user", "content": "Write a short Python function to calculate fibonacci numbers"}
    ],
    stream=True
)

# Print each chunk as it arrives
print("Gemini: ", end="", flush=True)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()  # New line at the end
```

### CLI Usage

Test your installation with the command-line interface:

=== "Basic Query"

    ```bash
    claif-gem query "What is machine learning?"
    ```

=== "Interactive Chat"

    ```bash
    claif-gem chat --model gemini-1.5-pro
    ```

=== "With System Prompt"

    ```bash
    claif-gem query "Translate to Spanish: Hello, how are you?" \
      --system "You are a professional translator"
    ```

## 🛠️ Configuration Verification

### Health Check

Verify everything is working correctly:

```python
from claif_gem import GeminiClient

try:
    client = GeminiClient()
    response = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "Hello!"}],
        max_tokens=10
    )
    print("✅ claif_gem is working correctly!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### CLI Health Check

```bash
# Check if everything is properly configured
claif-gem query "Hello!" --show-metrics

# List available models
claif-gem models

# Show current configuration
claif-gem config show
```

## 🎮 Common Usage Patterns

### 1. Code Generation

```python
from claif_gem import GeminiClient

client = GeminiClient()

response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "system", "content": "You are a helpful coding assistant."},
        {"role": "user", "content": "Write a Python function to merge two sorted lists"}
    ],
    temperature=0.3  # Lower temperature for more consistent code
)

print(response.choices[0].message.content)
```

### 2. Creative Writing

```python
from claif_gem import GeminiClient

client = GeminiClient()

response = client.chat.completions.create(
    model="gemini-1.5-pro",
    messages=[
        {"role": "user", "content": "Write a creative short story about a robot learning to paint"}
    ],
    temperature=0.9,  # Higher temperature for creativity
    max_tokens=500
)

print(response.choices[0].message.content)
```

### 3. Data Analysis

```python
from claif_gem import GeminiClient

client = GeminiClient()

data = """
Q1 Sales: $50,000
Q2 Sales: $65,000  
Q3 Sales: $45,000
Q4 Sales: $78,000
"""

response = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=[
        {"role": "system", "content": "You are a data analyst. Provide insights in a structured format."},
        {"role": "user", "content": f"Analyze this sales data:\n{data}"}
    ]
)

print(response.choices[0].message.content)
```

### 4. Multi-turn Conversation

```python
from claif_gem import GeminiClient

client = GeminiClient()

# Build conversation history
messages = [
    {"role": "system", "content": "You are a helpful Python tutor."},
    {"role": "user", "content": "What are Python list comprehensions?"},
]

# First response
response1 = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=messages
)

# Add assistant response to history
messages.append({
    "role": "assistant", 
    "content": response1.choices[0].message.content
})

# Continue conversation
messages.append({
    "role": "user", 
    "content": "Can you show me a practical example?"
})

response2 = client.chat.completions.create(
    model="gemini-1.5-flash",
    messages=messages
)

print("First response:")
print(response1.choices[0].message.content)
print("\nSecond response:")
print(response2.choices[0].message.content)
```

## 🔧 Model Selection Guide

| Model | Best For | Context | Speed | Cost |
|-------|----------|---------|-------|------|
| `gemini-1.5-flash` | Quick responses, simple tasks | 1M tokens | ⚡⚡⚡ | 💰 |
| `gemini-1.5-flash-8b` | Lightweight operations | 1M tokens | ⚡⚡⚡⚡ | 💰 |
| `gemini-1.5-pro` | Complex reasoning, analysis | 2M tokens | ⚡⚡ | 💰💰 |
| `gemini-2.0-flash-exp` | Latest features, experimental | 1M tokens | ⚡⚡⚡ | 💰 |

### Model Selection Examples

```python
# For quick questions and simple tasks
response = client.chat.completions.create(
    model="gemini-1.5-flash",  # Fast and efficient
    messages=[{"role": "user", "content": "What's the weather like today?"}]
)

# For complex analysis and reasoning
response = client.chat.completions.create(
    model="gemini-1.5-pro",  # More powerful
    messages=[{"role": "user", "content": "Analyze the economic implications of..."}]
)

# For experimental features
response = client.chat.completions.create(
    model="gemini-2.0-flash-exp",  # Latest capabilities
    messages=[{"role": "user", "content": "Use advanced reasoning for..."}]
)
```

## 🚨 Troubleshooting

### Common Issues

!!! error "CLI Not Found"
    ```
    FileNotFoundError: Gemini CLI not found
    ```
    
    **Solution:** Install the Gemini CLI:
    ```bash
    npm install -g @google/gemini-cli
    ```

!!! error "API Key Missing"
    ```
    Error: API key not found
    ```
    
    **Solution:** Set your API key:
    ```bash
    export GEMINI_API_KEY="your-api-key"
    ```

!!! error "Permission Denied"
    ```
    PermissionError: [Errno 13] Permission denied
    ```
    
    **Solution:** Fix CLI permissions:
    ```bash
    chmod +x $(which gemini)
    ```

### Verification Commands

```bash
# Check if Gemini CLI is installed
which gemini

# Test Gemini CLI directly
gemini "Hello!" --model gemini-1.5-flash

# Test claif_gem installation
python -c "import claif_gem; print('✅ Installed successfully')"

# Test API key
claif-gem query "Hello!" --show-metrics
```

## ⏭️ Next Steps

🎉 **Congratulations!** You now have `claif_gem` up and running.

### Continue Learning

1. **[Installation Guide](installation.md)** - Detailed installation options and troubleshooting
2. **[Usage Guide](usage.md)** - Comprehensive examples and advanced patterns  
3. **[Configuration](configuration.md)** - Customize behavior and settings
4. **[CLI Reference](cli-reference.md)** - Master the command-line interface

### Advanced Topics

- **Batch Processing** - Handle multiple requests efficiently
- **Error Handling** - Robust error recovery strategies
- **Custom Models** - Use specific model configurations
- **Integration Patterns** - Embed in larger applications

### Join the Community

- 📖 [Read the full documentation](index.md)
- 🐛 [Report issues](https://github.com/twardoch/claif_gem/issues)
- 💬 [Join discussions](https://github.com/twardoch/claif_gem/discussions)
- 🤝 [Contribute to the project](contributing.md)

---

**Happy coding with claif_gem! 🚀**