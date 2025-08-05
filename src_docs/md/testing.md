# Testing Guide

Comprehensive testing guide for `claif_gem`. Learn testing strategies, setup procedures, and best practices for ensuring code quality and reliability.

## 🎯 Testing Overview

### Testing Philosophy

`claif_gem` employs a multi-layered testing strategy:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **End-to-End Tests** - Test complete workflows
4. **Mock Tests** - Test without external dependencies
5. **Performance Tests** - Measure performance and load capacity

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_client.py      # Client component tests
│   ├── test_config.py      # Configuration tests
│   ├── test_transport.py   # Transport layer tests
│   └── test_types.py       # Type system tests
├── integration/            # Integration tests
│   ├── test_cli_integration.py
│   └── test_api_integration.py
├── e2e/                    # End-to-end tests
│   ├── test_workflows.py
│   └── test_scenarios.py
├── performance/            # Performance tests
│   ├── test_load.py
│   └── test_benchmarks.py
├── fixtures/               # Test fixtures and data
│   ├── responses/
│   └── configs/
├── conftest.py            # Pytest configuration
└── utils.py               # Test utilities
```

## 🛠️ Test Environment Setup

### Development Dependencies

Install testing dependencies:

```bash
# Install with test dependencies
pip install -e ".[test]"

# Or install individual packages
pip install pytest pytest-cov pytest-mock pytest-asyncio coverage
```

### Test Configuration

#### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=src/claif_gem
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    slow: Slow tests (may take >1s)
    network: Tests requiring network access
    cli: Tests requiring Gemini CLI
```

#### conftest.py

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock, patch
from claif_gem import GeminiClient
from claif_gem.config import GeminiConfig

@pytest.fixture
def mock_gemini_cli():
    """Mock Gemini CLI for testing."""
    with patch('claif_gem.client.subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"candidates": [{"content": {"parts": [{"text": "Test response"}]}}]}',
            stderr=''
        )
        yield mock_run

@pytest.fixture
def mock_cli_path():
    """Mock CLI path discovery."""
    with patch('claif_gem.client.shutil.which') as mock_which:
        mock_which.return_value = '/usr/local/bin/gemini'
        yield mock_which

@pytest.fixture
def test_config():
    """Test configuration."""
    return GeminiConfig(
        api_key="test-api-key",
        default_model="gemini-1.5-flash",
        timeout=60,
        verbose=True
    )

@pytest.fixture
def client(mock_cli_path, test_config):
    """Test client instance."""
    return GeminiClient(config=test_config)

@pytest.fixture
def sample_messages():
    """Sample message list for testing."""
    return [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
```

## 🧪 Unit Testing

### Testing the GeminiClient

#### Basic Client Tests

```python
# tests/unit/test_client.py
import pytest
from unittest.mock import Mock, patch
from claif_gem import GeminiClient
from claif_gem.exceptions import GeminiCLIError, GeminiTimeoutError

class TestGeminiClient:
    """Test suite for GeminiClient."""
    
    def test_client_initialization(self, test_config):
        """Test client initialization."""
        client = GeminiClient(config=test_config)
        assert client.api_key == "test-api-key"
        assert client.timeout == 60
    
    def test_client_initialization_with_params(self, mock_cli_path):
        """Test client initialization with direct parameters."""
        client = GeminiClient(
            api_key="direct-key",
            timeout=300
        )
        assert client.api_key == "direct-key"
        assert client.timeout == 300
    
    @patch.dict('os.environ', {'GEMINI_API_KEY': 'env-key'})
    def test_client_api_key_from_env(self, mock_cli_path):
        """Test API key loading from environment."""
        client = GeminiClient()
        assert client.api_key == "env-key"
    
    def test_cli_path_discovery(self):
        """Test CLI path discovery logic."""
        with patch('claif_gem.client.shutil.which') as mock_which:
            mock_which.return_value = '/usr/local/bin/gemini'
            client = GeminiClient()
            assert client._gemini_cli_path == '/usr/local/bin/gemini'
    
    def test_cli_not_found_error(self):
        """Test error when CLI is not found."""
        with patch('claif_gem.client.shutil.which', return_value=None):
            with pytest.raises(FileNotFoundError, match="Gemini CLI not found"):
                GeminiClient()

class TestChatCompletions:
    """Test suite for chat completions."""
    
    def test_basic_completion(self, client, mock_gemini_cli, sample_messages):
        """Test basic chat completion."""
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=sample_messages
        )
        
        assert response.choices[0].message.content == "Test response"
        assert response.model == "gemini-1.5-flash"
        assert response.usage.total_tokens > 0
        
        # Verify CLI was called
        mock_gemini_cli.assert_called_once()
        call_args = mock_gemini_cli.call_args[0][0]
        assert "gemini" in call_args[0]
    
    def test_model_name_mapping(self, client, mock_gemini_cli):
        """Test OpenAI model name mapping."""
        client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "test"}]
        )
        
        call_args = mock_gemini_cli.call_args[0][0]
        assert "--model" in call_args
        model_index = call_args.index("--model") + 1
        assert call_args[model_index] == "gemini-1.5-pro"
    
    def test_temperature_parameter(self, client, mock_gemini_cli):
        """Test temperature parameter passing."""
        client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "test"}],
            temperature=0.9
        )
        
        call_args = mock_gemini_cli.call_args[0][0]
        assert "--temperature" in call_args
        temp_index = call_args.index("--temperature") + 1
        assert call_args[temp_index] == "0.9"
    
    def test_max_tokens_parameter(self, client, mock_gemini_cli):
        """Test max_tokens parameter passing."""
        client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=500
        )
        
        call_args = mock_gemini_cli.call_args[0][0]
        assert "--max-output-tokens" in call_args
        tokens_index = call_args.index("--max-output-tokens") + 1
        assert call_args[tokens_index] == "500"
    
    def test_streaming_completion(self, client, mock_gemini_cli, sample_messages):
        """Test streaming completion."""
        stream = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=sample_messages,
            stream=True
        )
        
        chunks = list(stream)
        assert len(chunks) > 0
        
        # Check first chunk has role
        assert chunks[0].choices[0].delta.role == "assistant"
        
        # Check content chunks
        content_chunks = [
            chunk for chunk in chunks 
            if chunk.choices[0].delta.content
        ]
        assert len(content_chunks) > 0
        
        # Check final chunk
        assert chunks[-1].choices[0].finish_reason == "stop"
    
    def test_cli_error_handling(self, client, sample_messages):
        """Test CLI error handling."""
        with patch('claif_gem.client.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, ['gemini'], stderr="API error"
            )
            
            with pytest.raises(RuntimeError, match="Gemini CLI error"):
                client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=sample_messages
                )
    
    def test_timeout_handling(self, client, sample_messages):
        """Test timeout handling."""
        with patch('claif_gem.client.subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                ['gemini'], timeout=60
            )
            
            with pytest.raises(TimeoutError, match="timed out after 60 seconds"):
                client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=sample_messages
                )
```

### Testing Configuration

```python
# tests/unit/test_config.py
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from claif_gem.config import GeminiConfig

class TestGeminiConfig:
    """Test suite for configuration management."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GeminiConfig()
        assert config.default_model == "gemini-1.5-flash"
        assert config.temperature == 0.7
        assert config.timeout == 120
        assert config.auto_approve is True
    
    def test_config_from_dict(self):
        """Test configuration creation from dictionary."""
        config_dict = {
            "default_model": "gemini-1.5-pro",
            "temperature": 0.5,
            "timeout": 300
        }
        config = GeminiConfig.from_dict(config_dict)
        assert config.default_model == "gemini-1.5-pro"
        assert config.temperature == 0.5
        assert config.timeout == 300
    
    def test_config_to_dict(self):
        """Test configuration conversion to dictionary."""
        config = GeminiConfig(
            default_model="gemini-1.5-pro",
            temperature=0.5
        )
        config_dict = config.to_dict()
        assert config_dict["default_model"] == "gemini-1.5-pro"
        assert config_dict["temperature"] == 0.5
    
    def test_config_file_operations(self):
        """Test configuration file save/load operations."""
        config = GeminiConfig(
            default_model="gemini-1.5-pro",
            temperature=0.5,
            timeout=300
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config.save_to_file(f.name)
            
            # Load and verify
            loaded_config = GeminiConfig.from_file(f.name)
            assert loaded_config.default_model == "gemini-1.5-pro"
            assert loaded_config.temperature == 0.5
            assert loaded_config.timeout == 300
        
        # Cleanup
        Path(f.name).unlink()
    
    def test_invalid_config_file(self):
        """Test handling of invalid configuration file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            f.flush()
            
            with pytest.raises(ValueError):
                GeminiConfig.from_file(f.name)
        
        Path(f.name).unlink()
    
    def test_nonexistent_config_file(self):
        """Test handling of nonexistent configuration file."""
        with pytest.raises(FileNotFoundError):
            GeminiConfig.from_file("/nonexistent/path/config.json")
    
    @patch.dict('os.environ', {
        'GEMINI_API_KEY': 'env-api-key',
        'GEMINI_DEFAULT_MODEL': 'gemini-1.5-pro',
        'GEMINI_DEFAULT_TEMPERATURE': '0.8'
    })
    def test_config_from_environment(self):
        """Test configuration loading from environment variables."""
        config = GeminiConfig.from_environment()
        assert config.api_key == "env-api-key"
        assert config.default_model == "gemini-1.5-pro"
        assert config.temperature == 0.8
```

### Testing Transport Layer

```python
# tests/unit/test_transport.py
import pytest
import subprocess
from unittest.mock import Mock, patch
from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiOptions
from claif_gem.exceptions import GeminiCLIError, GeminiTimeoutError

class TestGeminiTransport:
    """Test suite for transport layer."""
    
    def test_command_building(self):
        """Test CLI command building."""
        transport = GeminiTransport("/usr/local/bin/gemini")
        options = GeminiOptions(
            model="gemini-1.5-pro",
            temperature=0.8,
            max_tokens=500
        )
        
        cmd = transport.build_command("Hello!", options)
        
        assert cmd[0] == "/usr/local/bin/gemini"
        assert "--model" in cmd
        assert "gemini-1.5-pro" in cmd
        assert "--temperature" in cmd
        assert "0.8" in cmd
        assert "--max-output-tokens" in cmd
        assert "500" in cmd
        assert "Hello!" in cmd
    
    def test_response_parsing_json(self):
        """Test JSON response parsing."""
        transport = GeminiTransport("/usr/local/bin/gemini")
        json_response = '''
        {
            "candidates": [{
                "content": {
                    "parts": [{"text": "Hello, how can I help you?"}]
                }
            }]
        }
        '''
        
        parsed = transport.parse_response(json_response)
        assert parsed == "Hello, how can I help you?"
    
    def test_response_parsing_plain_text(self):
        """Test plain text response parsing."""
        transport = GeminiTransport("/usr/local/bin/gemini")
        text_response = "Hello, how can I help you?"
        
        parsed = transport.parse_response(text_response)
        assert parsed == "Hello, how can I help you?"
    
    def test_cli_execution_success(self):
        """Test successful CLI execution."""
        transport = GeminiTransport("/usr/local/bin/gemini")
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Test response",
                stderr=""
            )
            
            result = transport.execute_sync(["gemini", "Hello!"])
            assert result == "Test response"
            mock_run.assert_called_once()
    
    def test_cli_execution_failure(self):
        """Test CLI execution failure."""
        transport = GeminiTransport("/usr/local/bin/gemini")
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(
                1, ["gemini"], stderr="API error"
            )
            
            with pytest.raises(GeminiCLIError, match="API error"):
                transport.execute_sync(["gemini", "Hello!"])
    
    def test_cli_timeout(self):
        """Test CLI timeout handling."""
        transport = GeminiTransport("/usr/local/bin/gemini", timeout=30)
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(
                ["gemini"], timeout=30
            )
            
            with pytest.raises(GeminiTimeoutError):
                transport.execute_sync(["gemini", "Hello!"])
    
    def test_cli_not_found(self):
        """Test CLI not found error."""
        transport = GeminiTransport("/nonexistent/gemini")
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            
            with pytest.raises(GeminiCLIError, match="not found"):
                transport.execute_sync(["gemini", "Hello!"])
```

## 🔗 Integration Testing

### API Integration Tests

```python
# tests/integration/test_api_integration.py
import pytest
from claif_gem import GeminiClient
from claif_gem.config import GeminiConfig

@pytest.mark.integration
class TestAPIIntegration:
    """Integration tests for API functionality."""
    
    @pytest.fixture
    def integration_client(self):
        """Client for integration testing."""
        # Only run if API key is available
        pytest.importorskip("os").environ.get("GEMINI_API_KEY") or \
            pytest.skip("GEMINI_API_KEY not set")
        
        return GeminiClient(timeout=30)
    
    def test_basic_completion_integration(self, integration_client):
        """Test basic completion with real API."""
        response = integration_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "Say 'Hello, World!'"}],
            max_tokens=10
        )
        
        assert response.choices[0].message.content
        assert response.model == "gemini-1.5-flash"
        assert response.usage.total_tokens > 0
    
    def test_streaming_integration(self, integration_client):
        """Test streaming with real API."""
        stream = integration_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[{"role": "user", "content": "Count to 3"}],
            stream=True,
            max_tokens=20
        )
        
        chunks = list(stream)
        assert len(chunks) > 0
        
        # Verify streaming structure
        assert chunks[0].choices[0].delta.role == "assistant"
        assert chunks[-1].choices[0].finish_reason == "stop"
    
    def test_system_prompt_integration(self, integration_client):
        """Test system prompt functionality."""
        response = integration_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "system", "content": "Respond only with 'OK'"},
                {"role": "user", "content": "Hello"}
            ],
            max_tokens=5
        )
        
        assert "OK" in response.choices[0].message.content.upper()
    
    @pytest.mark.slow
    def test_long_conversation_integration(self, integration_client):
        """Test multi-turn conversation."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is 2+2?"},
        ]
        
        # First exchange
        response1 = integration_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            max_tokens=20
        )
        
        messages.append({
            "role": "assistant", 
            "content": response1.choices[0].message.content
        })
        messages.append({
            "role": "user", 
            "content": "What about 3+3?"
        })
        
        # Second exchange
        response2 = integration_client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            max_tokens=20
        )
        
        assert response2.choices[0].message.content
        assert response2.usage.total_tokens > response1.usage.total_tokens
```

### CLI Integration Tests

```python
# tests/integration/test_cli_integration.py
import pytest
import subprocess
from claif_gem.cli import CLI

@pytest.mark.integration
@pytest.mark.cli
class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_cli_query_command(self):
        """Test CLI query command."""
        result = subprocess.run([
            "claif-gem", "query", "Say hello", 
            "--max-tokens", "5"
        ], capture_output=True, text=True, timeout=30)
        
        assert result.returncode == 0
        assert len(result.stdout) > 0
    
    def test_cli_models_command(self):
        """Test CLI models command."""
        result = subprocess.run([
            "claif-gem", "models"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "gemini" in result.stdout.lower()
    
    def test_cli_config_show(self):
        """Test CLI config show command."""
        result = subprocess.run([
            "claif-gem", "config", "show"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
    
    def test_cli_version_command(self):
        """Test CLI version command."""
        result = subprocess.run([
            "claif-gem", "version"
        ], capture_output=True, text=True, timeout=10)
        
        assert result.returncode == 0
        assert "claif-gem" in result.stdout
    
    def test_cli_health_command(self):
        """Test CLI health command."""
        result = subprocess.run([
            "claif-gem", "health"
        ], capture_output=True, text=True, timeout=15)
        
        assert result.returncode == 0
```

## 🚀 End-to-End Testing

### Workflow Tests

```python
# tests/e2e/test_workflows.py
import pytest
import tempfile
from pathlib import Path
from claif_gem import GeminiClient
from claif_gem.config import GeminiConfig

@pytest.mark.e2e
class TestCompleteWorkflows:
    """End-to-end workflow tests."""
    
    def test_complete_setup_workflow(self):
        """Test complete setup and usage workflow."""
        # 1. Create configuration
        config = GeminiConfig(
            api_key=os.environ.get("GEMINI_API_KEY", "test-key"),
            default_model="gemini-1.5-flash",
            timeout=30
        )
        
        # 2. Save configuration to file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config.save_to_file(f.name)
            config_path = f.name
        
        try:
            # 3. Load configuration from file
            loaded_config = GeminiConfig.from_file(config_path)
            assert loaded_config.default_model == "gemini-1.5-flash"
            
            # 4. Create client with loaded configuration
            client = GeminiClient(config=loaded_config)
            
            # 5. Test basic functionality (with mocking if no API key)
            if not os.environ.get("GEMINI_API_KEY"):
                with patch('claif_gem.client.subprocess.run') as mock_run:
                    mock_run.return_value = Mock(
                        returncode=0,
                        stdout="Test response",
                        stderr=""
                    )
                    
                    response = client.chat.completions.create(
                        model="gemini-1.5-flash",
                        messages=[{"role": "user", "content": "Hello"}]
                    )
                    assert response.choices[0].message.content == "Test response"
            
        finally:
            Path(config_path).unlink()
    
    def test_error_recovery_workflow(self):
        """Test error recovery workflow."""
        # 1. Try with invalid CLI path
        with pytest.raises(FileNotFoundError):
            GeminiClient(cli_path="/nonexistent/path")
        
        # 2. Try with valid path but mock failure
        with patch('claif_gem.client.shutil.which', return_value='/usr/local/bin/gemini'):
            client = GeminiClient()
            
            with patch('claif_gem.client.subprocess.run') as mock_run:
                mock_run.side_effect = subprocess.CalledProcessError(
                    1, ['gemini'], stderr="API quota exceeded"
                )
                
                # 3. Expect error
                with pytest.raises(RuntimeError, match="API quota exceeded"):
                    client.chat.completions.create(
                        model="gemini-1.5-flash",
                        messages=[{"role": "user", "content": "Hello"}]
                    )
    
    @pytest.mark.slow
    def test_batch_processing_workflow(self):
        """Test batch processing workflow."""
        queries = [
            "What is 1+1?",
            "What is 2+2?", 
            "What is 3+3?"
        ]
        
        client = GeminiClient()
        results = []
        
        with patch('claif_gem.client.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Test response",
                stderr=""
            )
            
            for query in queries:
                response = client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=[{"role": "user", "content": query}],
                    max_tokens=10
                )
                results.append(response.choices[0].message.content)
        
        assert len(results) == len(queries)
        assert all(result == "Test response" for result in results)
```

## 📊 Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import time
import concurrent.futures
from claif_gem import GeminiClient

@pytest.mark.performance
class TestPerformance:
    """Performance and load tests."""
    
    def test_single_request_performance(self, benchmark):
        """Benchmark single request performance."""
        client = GeminiClient()
        
        with patch('claif_gem.client.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Benchmark response",
                stderr=""
            )
            
            def make_request():
                return client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=[{"role": "user", "content": "Hello"}]
                )
            
            result = benchmark(make_request)
            assert result.choices[0].message.content == "Benchmark response"
    
    def test_concurrent_requests(self):
        """Test concurrent request handling."""
        client = GeminiClient()
        num_requests = 10
        
        with patch('claif_gem.client.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Concurrent response",
                stderr=""
            )
            
            def make_request(i):
                return client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=[{"role": "user", "content": f"Request {i}"}]
                )
            
            start_time = time.time()
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_requests)]
                results = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            end_time = time.time()
            
            assert len(results) == num_requests
            assert all(r.choices[0].message.content == "Concurrent response" for r in results)
            
            # Should complete in reasonable time
            total_time = end_time - start_time
            assert total_time < 10  # Adjust based on expected performance
    
    def test_memory_usage(self):
        """Test memory usage patterns."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        client = GeminiClient()
        
        with patch('claif_gem.client.subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="Memory test response",
                stderr=""
            )
            
            # Make multiple requests
            for i in range(100):
                client.chat.completions.create(
                    model="gemini-1.5-flash",
                    messages=[{"role": "user", "content": f"Request {i}"}]
                )
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (adjust threshold as needed)
        assert memory_increase < 50 * 1024 * 1024  # 50MB
    
    def test_cli_discovery_performance(self, benchmark):
        """Benchmark CLI discovery performance."""
        def discover_cli():
            with patch('claif_gem.client.shutil.which', return_value='/usr/local/bin/gemini'):
                client = GeminiClient()
                return client._gemini_cli_path
        
        result = benchmark(discover_cli)
        assert result == '/usr/local/bin/gemini'
```

### Benchmark Tests

```python
# tests/performance/test_benchmarks.py
import pytest
from unittest.mock import Mock, patch
from claif_gem import GeminiClient

@pytest.mark.performance
class TestBenchmarks:
    """Benchmark tests for various operations."""
    
    def test_client_initialization_benchmark(self, benchmark):
        """Benchmark client initialization."""
        def init_client():
            with patch('claif_gem.client.shutil.which', return_value='/usr/local/bin/gemini'):
                return GeminiClient()
        
        client = benchmark(init_client)
        assert client is not None
    
    def test_command_building_benchmark(self, benchmark):
        """Benchmark command building."""
        from claif_gem.transport import GeminiTransport
        from claif_gem.types import GeminiOptions
        
        transport = GeminiTransport("/usr/local/bin/gemini")
        options = GeminiOptions(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_tokens=500
        )
        
        def build_cmd():
            return transport.build_command("Test prompt", options)
        
        cmd = benchmark(build_cmd)
        assert "gemini" in cmd[0]
    
    def test_response_parsing_benchmark(self, benchmark):
        """Benchmark response parsing."""
        from claif_gem.transport import GeminiTransport
        
        transport = GeminiTransport("/usr/local/bin/gemini")
        json_response = '''
        {
            "candidates": [{
                "content": {
                    "parts": [{"text": "This is a test response for benchmarking"}]
                }
            }]
        }
        '''
        
        def parse_response():
            return transport.parse_response(json_response)
        
        result = benchmark(parse_response)
        assert result == "This is a test response for benchmarking"
```

## 🎯 Test Execution

### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m unit
pytest -m integration  
pytest -m e2e
pytest -m performance

# Run with coverage
pytest --cov=src/claif_gem --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py -v

# Run specific test method
pytest tests/unit/test_client.py::TestGeminiClient::test_client_initialization -v

# Run tests with specific markers
pytest -m "not slow" -v  # Skip slow tests
pytest -m "not network" -v  # Skip network-dependent tests
```

### Continuous Integration

#### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.12, 3.13]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[test]"
    
    - name: Run unit tests
      run: pytest tests/unit -v --cov=src/claif_gem
    
    - name: Run integration tests
      env:
        GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
      run: pytest tests/integration -v
      continue-on-error: true  # Don't fail if no API key
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
```

### Test Data Management

#### Test Fixtures

```python
# tests/fixtures/responses.py
"""Test response fixtures."""

MOCK_RESPONSES = {
    "simple_greeting": {
        "candidates": [{
            "content": {
                "parts": [{"text": "Hello! How can I help you today?"}]
            }
        }]
    },
    
    "code_generation": {
        "candidates": [{
            "content": {
                "parts": [{
                    "text": "```python\ndef hello_world():\n    print('Hello, World!')\n```"
                }]
            }
        }]
    },
    
    "error_response": {
        "error": {
            "code": 400,
            "message": "Invalid request parameters"
        }
    }
}

def get_mock_response(key: str) -> str:
    """Get mock response by key."""
    import json
    return json.dumps(MOCK_RESPONSES[key])
```

## 📋 Testing Best Practices

### Test Organization

1. **Use descriptive test names** - `test_client_handles_timeout_gracefully`
2. **Group related tests** - Use test classes to organize related functionality
3. **Use fixtures** - Share common setup between tests
4. **Mark tests appropriately** - Use pytest markers for categorization
5. **Mock external dependencies** - Don't rely on external services in unit tests

### Test Data

1. **Use realistic test data** - Mirror production data patterns
2. **Test edge cases** - Empty inputs, very long inputs, special characters
3. **Test error conditions** - Network failures, invalid inputs, timeouts
4. **Use property-based testing** - For complex data validation

### Coverage Goals

- **Unit Tests**: 90%+ coverage
- **Integration Tests**: Cover all major workflows
- **E2E Tests**: Cover critical user journeys
- **Performance Tests**: Ensure acceptable performance

### Common Pitfalls

1. **Don't test implementation details** - Test behavior, not internals
2. **Avoid test interdependence** - Each test should be independent
3. **Don't over-mock** - Balance between isolation and realism
4. **Keep tests fast** - Unit tests should run in milliseconds
5. **Make tests deterministic** - Avoid time-dependent or random behavior

## ⏭️ Next Steps

Now that you understand testing:

1. **[Contributing Guide](contributing.md)** - Learn how to contribute to the project
2. **[API Reference](api-reference.md)** - Understand the complete API
3. **[Architecture Guide](architecture.md)** - Learn the internal design
4. **[Usage Guide](usage.md)** - See practical examples

---

**Testing Questions?** Check our [discussions](https://github.com/twardoch/claif_gem/discussions) or [open an issue](https://github.com/twardoch/claif_gem/issues).