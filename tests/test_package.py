# this_file: tests/test_package.py
"""Test suite for claif_gem."""

import claif_gem
import pytest
from unittest.mock import patch

from claif_gem.transport import GeminiTransport
from claif_gem.types import (
    GeminiOptions,
    GeminiMessage,
    ResultMessage,
)
from claif.common.types import TransportError, TextBlock


def test_version():
    """Verify package exposes version."""
    assert claif_gem.__version__


@pytest.mark.asyncio
class TestGeminiTransport:
    """Test suite for GeminiTransport."""

    @pytest.fixture
    def transport(self):
        """Fixture for a GeminiTransport instance."""
        return GeminiTransport()

    def test_initialization(self, transport):
        """Test that the transport initializes correctly."""
        assert transport.process is None
        assert transport.session_id is not None

    @patch("claif_gem.transport.find_executable", return_value="gemini-cli")
    def test_build_command_simple(self, mock_find_cli, transport):
        """Test _build_command with simple prompt."""
        prompt = "Hello"
        options = GeminiOptions(auto_approve=False, yes_mode=False)
        command = transport._build_command(prompt, options)
        assert command == ["gemini-cli", "-p", "Hello"]

    @patch("claif_gem.transport.find_executable", return_value="gemini-cli")
    def test_build_command_with_options(self, mock_find_cli, transport):
        """Test _build_command with various options."""
        prompt = "test prompt"
        options = GeminiOptions(
            model="gemini-pro",
            temperature=0.8,
            system_prompt="You are a bot.",
            max_context_length=1024,
            images=["/path/to/image.jpg"],
            verbose=True,
            auto_approve=True,
        )
        command = transport._build_command(prompt, options)
        expected = [
            "gemini-cli",
            "-y",
            "-d",
            "-m",
            "gemini-pro",
            "-t",
            "0.8",
            "-s",
            "You are a bot.",
            "--max-context",
            "1024",
            "-p",
            "test prompt",
            "-i",
            "/path/to/image.jpg",
        ]
        assert command == expected

    @patch(
        "claif_gem.transport.shlex.split",
        return_value=["deno", "run", "script.js"],
    )
    @patch("claif_gem.transport.Path.exists", return_value=False)
    @patch(
        "claif_gem.transport.find_executable",
        return_value="deno run script.js",
    )
    def test_build_command_with_script(self, mock_find_cli, mock_exists, mock_shlex, transport):
        """Test _build_command with a script-based executable path."""
        prompt = "test"
        options = GeminiOptions(auto_approve=False, yes_mode=False)
        command = transport._build_command(prompt, options)
        assert command == ["deno", "run", "script.js", "-p", "test"]
        mock_shlex.assert_called_once_with("deno run script.js")

    @patch(
        "claif_gem.transport.find_executable",
        side_effect=TransportError("Not found"),
    )
    def test_find_cli_raises_error(self, mock_find_cli, transport):
        """Test that _find_cli raises TransportError when executable is not found."""
        with pytest.raises(TransportError, match="Not found"):
            transport._find_cli()

    async def test_send_query_success(self, transport, mocker):
        """Test send_query successfully returns a message."""

        async def mock_results():
            yield GeminiMessage(content="response")
            yield ResultMessage(error=False)

        mock_execute_query = mocker.patch.object(transport, "_execute_query", return_value=mock_results())

        results = [result async for result in transport.send_query("test", GeminiOptions(retry_count=0))]

        assert len(results) == 2
        assert len(results[0].content) == 1 and results[0].content[0].text == "response"
        assert not results[1].error
        mock_execute_query.assert_called_once()

    async def test_send_query_with_retry(self, transport, mocker):
        """Test that send_query retries on failure."""

        # First call fails, second succeeds
        async def first_call_results():
            raise TransportError("mocked error")
            yield  # This makes it an async generator

        async def second_call_results():
            yield GeminiMessage(content="response")
            yield ResultMessage(error=False)

        mock_execute_query = mocker.patch.object(
            transport,
            "_execute_query",
            side_effect=[first_call_results(), second_call_results()],
        )

        results = [result async for result in transport.send_query("test", GeminiOptions(retry_count=1))]

        assert mock_execute_query.call_count == 2
        assert len(results) == 2
        assert len(results[0].content) == 1 and results[0].content[0].text == "response"

    async def test_send_query_all_retries_fail(self, transport, mocker):
        """Test send_query when all retry attempts fail."""

        async def mock_failure():
            raise TransportError("mocked error")
            yield

        mock_execute_query = mocker.patch.object(transport, "_execute_query", return_value=mock_failure())

        results = [result async for result in transport.send_query("test", GeminiOptions(retry_count=2))]

        assert mock_execute_query.call_count == 3
        assert len(results) == 1
        assert results[0].error
        assert "failed after 2 retries" in results[0].message
