"""Edge case tests for claif_gem components."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from claif.common import TransportError
from claif.common.types import Message, MessageRole

from claif_gem.client import GeminiClient
from claif_gem.transport import GeminiTransport
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


class TestTransportEdgeCases:
    """Test edge cases for GeminiTransport."""

    @pytest.fixture
    def transport(self):
        """Create a transport instance."""
        return GeminiTransport()

    @pytest.mark.asyncio
    async def test_disconnect_process_already_none(self, transport):
        """Test disconnect when process is already None."""
        transport.process = None

        # Should not raise any exception
        await transport.disconnect()
        assert transport.process is None

    @pytest.mark.asyncio
    async def test_disconnect_process_wait_fails(self, transport):
        """Test disconnect when process wait fails."""
        mock_process = Mock()
        mock_process.terminate = Mock()
        mock_process.wait = AsyncMock(side_effect=Exception("Wait failed"))

        transport.process = mock_process

        # Should not raise, just log the error
        await transport.disconnect()
        assert transport.process is None
        mock_process.terminate.assert_called_once()

    def test_build_command_with_extreme_temperature(self, transport):
        """Test command building with extreme temperature values."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            options = GeminiOptions(temperature=0.0)
            command = transport._build_command("Test", options)

            assert "-t" in command
            assert "0.0" in command

            options = GeminiOptions(temperature=1.0)
            command = transport._build_command("Test", options)

            assert "-t" in command
            assert "1.0" in command

    def test_build_command_with_very_long_prompt(self, transport):
        """Test command building with very long prompt."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            long_prompt = "A" * 10000
            options = GeminiOptions()
            command = transport._build_command(long_prompt, options)

            assert "-p" in command
            assert long_prompt in command

    def test_build_command_with_special_characters(self, transport):
        """Test command building with special characters in prompt."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            special_prompt = 'Hello\nWorld\t"quoted"\\'
            options = GeminiOptions()
            command = transport._build_command(special_prompt, options)

            assert "-p" in command
            assert special_prompt in command

    def test_build_command_with_empty_images_list(self, transport):
        """Test command building with empty images list."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            options = GeminiOptions(images=[])
            command = transport._build_command("Test", options)

            # Should not include any -i flags
            assert "-i" not in command

    def test_build_command_with_single_image(self, transport):
        """Test command building with single image."""
        with patch("claif_gem.transport.find_executable", return_value="gemini"):
            options = GeminiOptions(images=["/path/to/image.jpg"])
            command = transport._build_command("Test", options)

            assert "-i" in command
            assert "/path/to/image.jpg" in command

    @pytest.mark.asyncio
    async def test_execute_query_malformed_json(self, transport, mock_subprocess):
        """Test execute_query with malformed JSON response."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'{"invalid": json}', b""))
        mock_subprocess.return_value = mock_process

        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()

        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)

        # Should treat as plain text when JSON parsing fails
        assert len(messages) == 2
        assert isinstance(messages[0], GeminiMessage)
        assert messages[0].content[0].text == '{"invalid": json}'

    @pytest.mark.asyncio
    async def test_execute_query_json_without_content(self, transport, mock_subprocess):
        """Test execute_query with JSON response missing content."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'{"role": "assistant"}', b""))
        mock_subprocess.return_value = mock_process

        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()

        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)

        # Should treat as plain text when required fields are missing
        assert len(messages) == 2
        assert isinstance(messages[0], GeminiMessage)
        assert messages[0].content[0].text == '{"role": "assistant"}'

    @pytest.mark.asyncio
    async def test_execute_query_json_with_empty_content(self, transport, mock_subprocess):
        """Test execute_query with JSON response with empty content."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'{"content": "", "role": "assistant"}', b""))
        mock_subprocess.return_value = mock_process

        command = ["gemini", "-p", "Test"]
        env = {"PATH": "/bin"}
        options = GeminiOptions()

        messages = []
        async for msg in transport._execute_query(command, env, options, "Test"):
            messages.append(msg)

        assert len(messages) == 2
        assert isinstance(messages[0], GeminiMessage)
        assert messages[0].content[0].text == ""

    @pytest.mark.asyncio
    async def test_send_query_with_zero_retries(self, transport):
        """Test send_query with zero retries."""

        async def mock_execute(*args):
            msg = "Network error"
            raise TransportError(msg)

        with patch.object(transport, "_execute_query", side_effect=mock_execute):
            options = GeminiOptions(retry_count=0)
            messages = []
            async for msg in transport.send_query("Test", options):
                messages.append(msg)

            assert len(messages) == 1
            assert isinstance(messages[0], ResultMessage)
            assert messages[0].error is True

    @pytest.mark.asyncio
    async def test_send_query_with_very_short_retry_delay(self, transport):
        """Test send_query with very short retry delay."""
        call_count = 0

        async def mock_execute(*args):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                msg = "Retryable error"
                raise TransportError(msg)
            yield GeminiMessage(content="Success")

        with patch.object(transport, "_execute_query", side_effect=mock_execute):
            options = GeminiOptions(retry_count=3, retry_delay=0.001)
            messages = []
            async for msg in transport.send_query("Test", options):
                messages.append(msg)

            assert call_count == 3
            assert len(messages) == 1
            assert isinstance(messages[0], GeminiMessage)


class TestClientEdgeCases:
    """Test edge cases for GeminiClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return GeminiClient()

    @pytest.mark.asyncio
    async def test_query_with_transport_that_yields_nothing(self, client):
        """Test query when transport yields nothing."""
        mock_transport = Mock()
        mock_transport.connect = AsyncMock()
        mock_transport.disconnect = AsyncMock()

        async def mock_send_query(*args):
            return
            yield  # Make it a generator but yield nothing

        mock_transport.send_query = mock_send_query
        client.transport = mock_transport

        messages = []
        async for msg in client.query("Test"):
            messages.append(msg)

        assert len(messages) == 0
        mock_transport.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_with_result_message_only(self, client):
        """Test query that yields only ResultMessage."""
        mock_transport = Mock()
        mock_transport.connect = AsyncMock()
        mock_transport.disconnect = AsyncMock()

        async def mock_send_query(*args):
            yield ResultMessage(error=False, message="No content")

        mock_transport.send_query = mock_send_query
        client.transport = mock_transport

        messages = []
        async for msg in client.query("Test"):
            messages.append(msg)

        assert len(messages) == 0  # ResultMessage should not be yielded to user

    @pytest.mark.asyncio
    async def test_query_with_mixed_message_types(self, client):
        """Test query that yields mixed message types."""
        mock_transport = Mock()
        mock_transport.connect = AsyncMock()
        mock_transport.disconnect = AsyncMock()

        async def mock_send_query(*args):
            yield GeminiMessage(content="First")
            yield ResultMessage(error=False, message="Middle result")
            yield GeminiMessage(content="Second")
            yield ResultMessage(error=False, message="Final result")

        mock_transport.send_query = mock_send_query
        client.transport = mock_transport

        messages = []
        async for msg in client.query("Test"):
            messages.append(msg)

        # Should only yield GeminiMessage converted to Message
        assert len(messages) == 2
        assert all(isinstance(msg, Message) for msg in messages)
        assert messages[0].content[0].text == "First"
        assert messages[1].content[0].text == "Second"

    @pytest.mark.asyncio
    async def test_query_auto_install_with_import_error(self, client):
        """Test auto-install when import fails."""

        async def mock_send_query(*args):
            msg = "gemini not found"
            raise FileNotFoundError(msg)

        client.transport.send_query = mock_send_query
        client.transport.connect = AsyncMock()
        client.transport.disconnect = AsyncMock()

        with patch("claif_gem.client.install_gemini", side_effect=ImportError("claif not found")):
            with pytest.raises(Exception) as exc_info:
                async for _ in client.query("Test"):
                    pass

            assert "auto-install failed" in str(exc_info.value)
            assert "claif not found" in str(exc_info.value)


class TestTypesEdgeCases:
    """Test edge cases for type classes."""

    def test_gemini_options_with_edge_values(self):
        """Test GeminiOptions with edge case values."""
        options = GeminiOptions(
            temperature=0.0,
            max_context_length=1,
            retry_count=0,
            retry_delay=0.0,
            images=[],
        )

        assert options.temperature == 0.0
        assert options.max_context_length == 1
        assert options.retry_count == 0
        assert options.retry_delay == 0.0
        assert options.images == []

    def test_gemini_message_with_very_long_content(self):
        """Test GeminiMessage with very long content."""
        long_content = "A" * 100000
        msg = GeminiMessage(content=long_content)

        assert len(msg.content) == 1
        assert msg.content[0].text == long_content

    def test_gemini_message_with_unicode_content(self):
        """Test GeminiMessage with unicode content."""
        unicode_content = "Hello 世界 🌍 🚀"
        msg = GeminiMessage(content=unicode_content)

        assert len(msg.content) == 1
        assert msg.content[0].text == unicode_content

    def test_result_message_with_large_duration(self):
        """Test ResultMessage with large duration."""
        msg = ResultMessage(duration=999999.999)
        assert msg.duration == 999999.999

    def test_result_message_with_very_long_message(self):
        """Test ResultMessage with very long message."""
        long_message = "Error: " + "A" * 10000
        msg = ResultMessage(error=True, message=long_message)
        assert msg.message == long_message
        assert msg.error is True


class TestIntegrationEdgeCases:
    """Test edge cases for integration scenarios."""

    @pytest.mark.asyncio
    async def test_full_flow_with_connection_issues(self):
        """Test full flow with intermittent connection issues."""
        from claif_gem.client import GeminiClient

        client = GeminiClient()
        call_count = 0

        async def mock_send_query(*args):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "Connection lost"
                raise ConnectionError(msg)
            if call_count == 2:
                msg = "Timeout"
                raise TransportError(msg)
            yield GeminiMessage(content="Finally succeeded")

        with patch.object(client.transport, "send_query", side_effect=mock_send_query):
            with patch.object(client.transport, "connect", new_callable=AsyncMock):
                with patch.object(client.transport, "disconnect", new_callable=AsyncMock):
                    # First call should fail
                    with pytest.raises(ConnectionError):
                        async for _ in client.query("Test", GeminiOptions(no_retry=True)):
                            pass

                    # Reset call count for second test
                    call_count = 0

                    # With retries enabled, should eventually succeed
                    messages = []
                    async for msg in client.query("Test", GeminiOptions(retry_count=3)):
                        messages.append(msg)

                    assert len(messages) == 1
                    assert messages[0].content[0].text == "Finally succeeded"

    @pytest.mark.asyncio
    async def test_concurrent_queries(self):
        """Test concurrent queries to the same client."""
        from claif_gem.client import GeminiClient

        client = GeminiClient()

        async def mock_send_query(prompt, options):
            await asyncio.sleep(0.1)  # Simulate network delay
            yield GeminiMessage(content=f"Response to: {prompt}")

        with patch.object(client.transport, "send_query", side_effect=mock_send_query):
            with patch.object(client.transport, "connect", new_callable=AsyncMock):
                with patch.object(client.transport, "disconnect", new_callable=AsyncMock):
                    # Run multiple queries concurrently
                    async def query_task(prompt):
                        messages = []
                        async for msg in client.query(prompt):
                            messages.append(msg)
                        return messages

                    tasks = [
                        query_task("Query 1"),
                        query_task("Query 2"),
                        query_task("Query 3"),
                    ]

                    results = await asyncio.gather(*tasks)

                    assert len(results) == 3
                    assert all(len(result) == 1 for result in results)
                    assert "Query 1" in results[0][0].content[0].text
                    assert "Query 2" in results[1][0].content[0].text
                    assert "Query 3" in results[2][0].content[0].text
