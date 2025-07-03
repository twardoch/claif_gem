# this_file: tests/test_retry_logic.py
"""Test retry logic for quota and rate limit errors."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from claif.common import TransportError
from claif.common.types import TextBlock

from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


@pytest.mark.asyncio
async def test_retry_on_quota_exhausted():
    """Test that quota exhausted errors trigger retry."""
    transport = GeminiTransport()
    options = GeminiOptions(retry_count=3, retry_delay=0.1, verbose=True)

    # Mock the subprocess to fail with quota error first, then succeed
    with patch("asyncio.create_subprocess_exec") as mock_subprocess:
        # First call: quota error
        process1 = AsyncMock()
        process1.returncode = 1
        process1.communicate = AsyncMock(return_value=(b"", b"Resource has been exhausted (e.g. check quota)."))

        # Second call: success
        process2 = AsyncMock()
        process2.returncode = 0
        process2.communicate = AsyncMock(return_value=(b"Test response", b""))

        mock_subprocess.side_effect = [process1, process2]

        messages = []
        async for msg in transport.send_query("test prompt", options):
            messages.append(msg)

        # Should have retried and succeeded
        assert len(messages) == 2
        assert isinstance(messages[0], GeminiMessage)
        assert len(messages[0].content) == 1
        assert messages[0].content[0].text == "Test response"
        assert isinstance(messages[1], ResultMessage)
        assert not messages[1].error


@pytest.mark.asyncio
async def test_retry_on_rate_limit():
    """Test that rate limit errors trigger retry."""
    transport = GeminiTransport()
    options = GeminiOptions(retry_count=2, retry_delay=0.1)

    with patch("asyncio.create_subprocess_exec") as mock_subprocess:
        # First call: rate limit error
        process1 = AsyncMock()
        process1.returncode = 1
        process1.communicate = AsyncMock(return_value=(b"", b"Error 429: Too many requests"))

        # Second call: success
        process2 = AsyncMock()
        process2.returncode = 0
        process2.communicate = AsyncMock(return_value=(b"Success", b""))

        mock_subprocess.side_effect = [process1, process2]

        messages = []
        async for msg in transport.send_query("test", options):
            messages.append(msg)

        assert len(messages) == 2
        assert len(messages[0].content) == 1
        assert messages[0].content[0].text == "Success"


@pytest.mark.asyncio
async def test_no_retry_flag():
    """Test that no_retry flag disables retries."""
    transport = GeminiTransport()
    options = GeminiOptions(retry_count=3, no_retry=True)

    with patch("asyncio.create_subprocess_exec") as mock_subprocess:
        process = AsyncMock()
        process.returncode = 1
        process.communicate = AsyncMock(return_value=(b"", b"Resource has been exhausted"))
        mock_subprocess.return_value = process

        messages = []
        async for msg in transport.send_query("test", options):
            messages.append(msg)

        # Should fail immediately without retry
        assert len(messages) == 1
        assert isinstance(messages[0], ResultMessage)
        assert messages[0].error
        assert "Resource has been exhausted" in messages[0].message

        # Should have been called only once
        assert mock_subprocess.call_count == 1


@pytest.mark.asyncio
async def test_max_retries_exceeded():
    """Test behavior when all retries are exhausted."""
    transport = GeminiTransport()
    options = GeminiOptions(retry_count=2, retry_delay=0.1)

    with patch("asyncio.create_subprocess_exec") as mock_subprocess:
        process = AsyncMock()
        process.returncode = 1
        process.communicate = AsyncMock(return_value=(b"", b"503 Service Unavailable"))
        mock_subprocess.return_value = process

        messages = []
        async for msg in transport.send_query("test", options):
            messages.append(msg)

        # Should get error after all retries
        assert len(messages) == 1
        assert isinstance(messages[0], ResultMessage)
        assert messages[0].error
        assert "failed after 2 retries" in messages[0].message

        # Should have tried 3 times (initial + 2 retries)
        assert mock_subprocess.call_count == 3


@pytest.mark.asyncio
async def test_non_retryable_error():
    """Test that non-retryable errors fail immediately."""
    transport = GeminiTransport()
    options = GeminiOptions(retry_count=3, retry_delay=0.1)

    with patch("asyncio.create_subprocess_exec") as mock_subprocess:
        process = AsyncMock()
        process.returncode = 1
        process.communicate = AsyncMock(return_value=(b"", b"Invalid API key"))
        mock_subprocess.return_value = process

        messages = []
        async for msg in transport.send_query("test", options):
            messages.append(msg)

        # Should fail immediately without retry
        assert len(messages) == 1
        assert isinstance(messages[0], ResultMessage)
        assert messages[0].error
        assert "Invalid API key" in messages[0].message

        # Should have been called only once
        assert mock_subprocess.call_count == 1


if __name__ == "__main__":
    asyncio.run(pytest.main([__file__, "-v"]))
