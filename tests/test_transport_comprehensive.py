"""Comprehensive test suite for claif_gem transport layer."""

import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from claif.common.types import TransportError, TextBlock
from tenacity import RetryError

from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


class TestGeminiTransport:
    """Test suite for GeminiTransport."""

    @pytest.fixture
    def transport(self):
        """Create a transport instance."""
        return GeminiTransport()

    @pytest.fixture 
    def mock_subprocess(self):
        """Mock asyncio subprocess."""
        with patch("asyncio.create_subprocess_exec") as mock_create:
            yield mock_create

    def test_init(self):
        """Test transport initialization."""
        transport = GeminiTransport()
        assert transport.process is None
        assert transport.session_id is not None
        assert isinstance(transport.session_id, str)
        # UUID format check
        assert len(transport.session_id) == 36  # Standard UUID with dashes

    @pytest.mark.asyncio
    async def test_connect(self, transport):
        """Test connect is a no-op."""
        await transport.connect()  # Should not raise

    @pytest.mark.asyncio
    async def test_disconnect_no_process(self, transport):
        """Test disconnect when no process is running."""
        await transport.disconnect()  # Should not raise
        assert transport.process is None

    @pytest.mark.asyncio
    async def test_disconnect_with_process(self, transport):
        """Test disconnect with running process."""
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock()
        
        transport.process = mock_process
        await transport.disconnect()
        
        mock_process.terminate.assert_called_once()
        mock_process.wait.assert_called_once()
        assert transport.process is None

    @pytest.mark.asyncio
    async def test_disconnect_with_error(self, transport):
        """Test disconnect when process termination fails."""
        mock_process = Mock()
        mock_process.terminate = Mock(side_effect=Exception("Termination error"))
        
        transport.process = mock_process
        
        # Should not raise, just log
        await transport.disconnect()
        assert transport.process is None

    def test_build_command_minimal(self, transport):
        """Test command building with minimal options."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            options = GeminiOptions()
            command = transport._build_command("Hello", options)
            
            assert command == ["gemini", "-y", "-p", "Hello"]

    def test_build_command_with_all_options(self, transport):
        """Test command building with all options."""
        with patch("claif_gem.transport.find_executable", return_value="/usr/bin/gemini"):
            options = GeminiOptions(
                model="gemini-pro",
                temperature=0.7,
                system_prompt="You are helpful",
                max_context_length=2048,
                images=["/img1.png", "/img2.jpg"],
                verbose=True,
                auto_approve=True,
                yes_mode=True
            )
            command = transport._build_command("Test prompt", options)
            
            expected = [
                "/usr/bin/gemini",
                "-y",
                "-d",  # verbose mode
                "-m", "gemini-pro",
                "-t", "0.7",
                "-s", "You are helpful",
                "--max-context", "2048",
                "-p", "Test prompt",
                "-i", "/img1.png",
                "-i", "/img2.jpg"
            ]
            assert command == expected

    def test_build_command_no_auto_approve(self, transport):
        """Test command without auto-approve."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            options = GeminiOptions(auto_approve=False, yes_mode=False)
            command = transport._build_command("Test", options)
            
            # Should not include -y flag
            assert command == ["gemini", "-p", "Test"]

    def test_build_command_with_shell_script(self, transport):
        """Test command with script path (e.g., 'deno run script.js')."""
        with patch("claif_gem.transport.find_executable", return_value="deno run /path/to/gemini.js"):
            with patch("claif_gem.transport.Path.exists", return_value=False):
                options = GeminiOptions()
                command = transport._build_command("Test", options)
                
                assert command[:3] == ["deno", "run", "/path/to/gemini.js"]
                assert "-y" in command
                assert "-p" in command
                assert "Test" in command

    def test_build_env(self, transport):
        """Test environment variable building."""
        with patch("claif_gem.transport.inject_claif_bin_to_path") as mock_inject:
            mock_inject.return_value = {"PATH": "/custom/bin:/usr/bin"}
            
            env = transport._build_env()
            
            assert env["GEMINI_CLI_INTERNAL"] == "1"
            assert env["CLAIF_PROVIDER"] == "gemini"
            assert env["PATH"] == "/custom/bin:/usr/bin"

    def test_build_env_import_error(self, transport):
        """Test environment building when claif import fails."""
        with patch("claif_gem.transport.inject_claif_bin_to_path", side_effect=ImportError):
            with patch("os.environ.copy", return_value={"PATH": "/bin"}):
                env = transport._build_env()
                
                assert env["GEMINI_CLI_INTERNAL"] == "1"
                assert env["CLAIF_PROVIDER"] == "gemini"
                assert env["PATH"] == "/bin"

    def test_find_cli_success(self, transport):
        """Test CLI finding success."""
        with patch("claif_gem.transport.find_executable", return_value="/opt/gemini/bin/gemini"):
            result = transport._find_cli()
            assert result == "/opt/gemini/bin/gemini"

    def test_find_cli_with_exec_path(self, transport):
        """Test CLI finding with explicit exec_path."""
        with patch("claif_gem.transport.find_executable", return_value="/custom/gemini"):
            result = transport._find_cli("/custom/gemini")
            assert result == "/custom/gemini"

    def test_find_cli_error(self, transport):
        """Test CLI finding error."""
        with patch("claif_gem.transport.find_executable", side_effect=TransportError("Not found")):
            with pytest.raises(TransportError, match="Not found"):
                transport._find_cli()

    @pytest.mark.asyncio
    async def test_execute_query_success_json(self, transport, mock_subprocess):
        """Test successful query execution with JSON response."""
        # Mock process
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b'{"content": "Hello from Gemini", "role": "assistant"}',
            b''
        ))
        mock_subprocess.return_value = mock_process
        
        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()
        
        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)
        
        assert len(messages) == 2
        assert len(isinstance(messages[0], GeminiMessage)
        assert messages[0].content) == 1 and isinstance(messages[0], GeminiMessage)
        assert messages[0].content[0].text == "Hello from Gemini"
        assert messages[0].role == "assistant"
        assert isinstance(messages[1], ResultMessage)
        assert messages[1].error is False

    @pytest.mark.asyncio
    async def test_execute_query_success_plain_text(self, transport, mock_subprocess):
        """Test successful query with plain text response."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b'Plain text response from Gemini',
            b''
        ))
        mock_subprocess.return_value = mock_process
        
        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()
        
        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)
        
        assert len(messages) == 2
        assert len(isinstance(messages[0], GeminiMessage)
        assert messages[0].content) == 1 and isinstance(messages[0], GeminiMessage)
        assert messages[0].content[0].text == "Plain text response from Gemini"
        assert isinstance(messages[1], ResultMessage)

    @pytest.mark.asyncio
    async def test_execute_query_error_non_retryable(self, transport, mock_subprocess):
        """Test query with non-retryable error."""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(
            b'',
            b'Invalid API key'
        ))
        mock_subprocess.return_value = mock_process
        
        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()
        
        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)
        
        assert len(messages) == 1
        assert isinstance(messages[0], ResultMessage)
        assert messages[0].error is True
        assert "Invalid API key" in messages[0].message

    @pytest.mark.asyncio
    async def test_execute_query_error_retryable(self, transport, mock_subprocess):
        """Test query with retryable error."""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(
            b'',
            b'Connection timeout'
        ))
        mock_subprocess.return_value = mock_process
        
        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()
        
        with pytest.raises(TransportError, match="retryable"):
            async for _ in transport._execute_query(command, env, options, "Test"):
                pass

    @pytest.mark.asyncio
    async def test_execute_query_empty_response(self, transport, mock_subprocess):
        """Test query with empty response."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'', b''))
        mock_subprocess.return_value = mock_process
        
        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()
        
        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)
        
        # Should yield ResultMessage only
        assert len(messages) == 1
        assert isinstance(messages[0], ResultMessage)
        assert messages[0].error is False

    @pytest.mark.asyncio
    async def test_send_query_no_retry(self, transport):
        """Test send_query with retry disabled."""
        with patch.object(transport, "_execute_query") as mock_execute:
            async def mock_execute_impl(*args):
                yield GeminiMessage(content="Response")
                yield ResultMessage(error=False)
            
            mock_execute.side_effect = mock_execute_impl
            
            options = GeminiOptions(no_retry=True)
            messages = []
            async for msg in transport.send_query("Test", options):
                messages.append(msg)
            
            assert len(messages) == 2
            assert isinstance(messages[0], GeminiMessage)
            assert isinstance(messages[1], ResultMessage)

    @pytest.mark.asyncio
    async def test_send_query_with_retry_success(self, transport):
        """Test send_query with retry that succeeds on second attempt."""
        call_count = 0
        
        async def mock_execute(*args):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise TransportError("Connection error")
            yield GeminiMessage(content="Success")
            yield ResultMessage(error=False)
        
        with patch.object(transport, "_execute_query", side_effect=mock_execute):
            options = GeminiOptions(retry_count=2, retry_delay=0.1)
            messages = []
            async for msg in transport.send_query("Test", options):
                messages.append(msg)
            
            assert call_count == 2
            assert len(messages) == 2
            assert len(messages[0].content) == 1 and messages[0].content[0].text == "Success"

    @pytest.mark.asyncio
    async def test_send_query_all_retries_fail(self, transport):
        """Test send_query when all retries fail."""
        async def mock_execute(*args):
            raise ConnectionError("Network error")
        
        with patch.object(transport, "_execute_query", side_effect=mock_execute):
            options = GeminiOptions(retry_count=2, retry_delay=0.1)
            messages = []
            async for msg in transport.send_query("Test", options):
                messages.append(msg)
            
            assert len(messages) == 1
            assert isinstance(messages[0], ResultMessage)
            assert messages[0].error is True
            assert "failed after 2 retries" in messages[0].message

    @pytest.mark.asyncio
    async def test_send_query_empty_response_error(self, transport):
        """Test send_query when response is empty."""
        async def mock_execute(*args):
            # Yield nothing - empty response
            return
            yield  # Make it a generator
        
        with patch.object(transport, "_execute_query", side_effect=mock_execute):
            options = GeminiOptions(retry_count=1, retry_delay=0.1)
            messages = []
            async for msg in transport.send_query("Test", options):
                messages.append(msg)
            
            # Should get error after retries
            assert len(messages) == 1
            assert isinstance(messages[0], ResultMessage)
            assert messages[0].error is True

    @pytest.mark.asyncio
    async def test_process_tracking(self, transport, mock_subprocess):
        """Test that process is properly tracked during execution."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            b'{"content": "Test"}',
            b''
        ))
        mock_subprocess.return_value = mock_process
        
        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()
        
        # Process should be None initially
        assert transport.process is None
        
        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)
            # Process should be set during execution
            if isinstance(msg, GeminiMessage):
                assert transport.process is mock_process
        
        # Process remains set after execution (cleanup happens in disconnect)
        assert transport.process is mock_process