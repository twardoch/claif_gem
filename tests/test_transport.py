
# this_file: claif_gem/tests/test_transport.py
"""Tests for the Gemini transport layer."""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch

from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiOptions, GeminiMessage, ResultMessage

@pytest.fixture
def mock_subprocess_exec():
    """Fixture to mock asyncio.create_subprocess_exec."""
    with patch('asyncio.create_subprocess_exec') as mock_exec:
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b'{"content": "test response"}', b'')
        mock_exec.return_value = mock_process
        yield mock_exec

@pytest.fixture
def mock_find_executable():
    """Fixture to mock find_executable."""
    with patch('claif_gem.transport.find_executable') as mock_find:
        mock_find.return_value = '/usr/local/bin/gemini'
        yield mock_find

@pytest.mark.asyncio
async def test_send_query_success(mock_subprocess_exec, mock_find_executable):
    """Test send_query with a successful response."""
    transport = GeminiTransport()
    options = GeminiOptions(verbose=False)
    prompt = "What is 1+1?"

    messages = [msg async for msg in transport.send_query(prompt, options)]

    # Assert that create_subprocess_exec was called with the correct command
    mock_subprocess_exec.assert_called_once()
    called_command = mock_subprocess_exec.call_args[0][0]
    assert called_command[0] == '/usr/local/bin/gemini'
    assert '-p' in called_command
    assert prompt in called_command

    # Assert the messages received
    assert len(messages) == 2
    assert isinstance(messages[0], GeminiMessage)
    assert messages[0].content == "test response"
    assert isinstance(messages[1], ResultMessage)
    assert not messages[1].error

@pytest.mark.asyncio
async def test_build_command_verbose():
    """Test _build_command with verbose option."""
    transport = GeminiTransport()
    options = GeminiOptions(verbose=True)
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '-d' in command

@pytest.mark.asyncio
async def test_build_command_model():
    """Test _build_command with model option."""
    transport = GeminiTransport()
    options = GeminiOptions(model="gemini-pro")
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '-m' in command
    assert 'gemini-pro' in command

@pytest.mark.asyncio
async def test_build_command_temperature():
    """Test _build_command with temperature option."""
    transport = GeminiTransport()
    options = GeminiOptions(temperature=0.5)
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '-t' in command
    assert '0.5' in command

@pytest.mark.asyncio
async def test_build_command_system_prompt():
    """Test _build_command with system_prompt option."""
    transport = GeminiTransport()
    options = GeminiOptions(system_prompt="You are a helpful assistant.")
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '-s' in command
    assert 'You are a helpful assistant.' in command

@pytest.mark.asyncio
async def test_build_command_max_context_length():
    """Test _build_command with max_context_length option."""
    transport = GeminiTransport()
    options = GeminiOptions(max_context_length=1024)
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '--max-context' in command
    assert '1024' in command

@pytest.mark.asyncio
async def test_build_command_auto_approve():
    """Test _build_command with auto_approve option."""
    transport = GeminiTransport()
    options = GeminiOptions(auto_approve=True)
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '-y' in command

@pytest.mark.asyncio
async def test_build_command_yes_mode():
    """Test _build_command with yes_mode option."""
    transport = GeminiTransport()
    options = GeminiOptions(yes_mode=True)
    prompt = "test prompt"

    command = transport._build_command(prompt, options)
    assert '-y' in command

@pytest.mark.asyncio
async def test_send_query_cli_error(mock_subprocess_exec, mock_find_executable):
    """Test send_query with a CLI error response."""
    transport = GeminiTransport()
    options = GeminiOptions()
    prompt = "test prompt"

    mock_subprocess_exec.return_value.returncode = 1
    mock_subprocess_exec.return_value.communicate.return_value = (b'', b'CLI error message')

    messages = [msg async for msg in transport.send_query(prompt, options)]

    assert len(messages) == 1
    assert isinstance(messages[0], ResultMessage)
    assert messages[0].error
    assert "CLI error message" in messages[0].message

@pytest.mark.asyncio
async def test_send_query_json_decode_error(mock_subprocess_exec, mock_find_executable):
    """Test send_query with invalid JSON output."""
    transport = GeminiTransport()
    options = GeminiOptions()
    prompt = "test prompt"

    mock_subprocess_exec.return_value.communicate.return_value = (b'invalid json', b'')

    messages = [msg async for msg in transport.send_query(prompt, options)]

    assert len(messages) == 2
    assert isinstance(messages[0], GeminiMessage)
    assert messages[0].content == "invalid json"
    assert isinstance(messages[1], ResultMessage)
    assert not messages[1].error

@pytest.mark.asyncio
async def test_disconnect_terminates_process():
    """Test that disconnect terminates the process."""
    transport = GeminiTransport()
    transport.process = AsyncMock()
    await transport.disconnect()
    transport.process.terminate.assert_called_once()
    transport.process.wait.assert_called_once()
    assert transport.process is None
