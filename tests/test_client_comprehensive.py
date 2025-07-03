"""Comprehensive test suite for claif_gem client."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from claif.common.types import Message, MessageRole, TextBlock

from claif_gem.client import GeminiClient, _get_client, _is_cli_missing_error, query
from claif_gem.types import GeminiMessage, GeminiOptions, ResultMessage


class TestHelperFunctions:
    """Test helper functions."""

    def test_is_cli_missing_error(self):
        """Test CLI missing error detection."""
        # Positive cases
        assert _is_cli_missing_error(Exception("command not found"))
        assert _is_cli_missing_error(Exception("No such file or directory"))
        assert _is_cli_missing_error(Exception("is not recognized as an internal or external command"))
        assert _is_cli_missing_error(Exception("Cannot find gemini"))
        assert _is_cli_missing_error(Exception("gemini not found"))
        assert _is_cli_missing_error(Exception("executable not found"))
        assert _is_cli_missing_error(Exception("Permission denied"))
        assert _is_cli_missing_error(FileNotFoundError("gemini"))

        # Negative cases
        assert not _is_cli_missing_error(Exception("API key invalid"))
        assert not _is_cli_missing_error(Exception("Network error"))
        assert not _is_cli_missing_error(Exception("Rate limit exceeded"))
        assert not _is_cli_missing_error(Exception("Model not available"))


class TestGeminiClient:
    """Test suite for GeminiClient."""

    @pytest.fixture
    def client(self):
        """Create a client instance."""
        return GeminiClient()

    @pytest.fixture
    def mock_transport(self):
        """Create a mock transport."""
        transport = MagicMock()
        transport.connect = AsyncMock()
        transport.disconnect = AsyncMock()
        transport.send_query = AsyncMock()
        return transport

    @pytest.mark.asyncio
    async def test_query_success(self, client, mock_transport):
        """Test successful query."""
        client.transport = mock_transport

        # Mock transport responses
        async def mock_send_query(prompt, options):
            yield GeminiMessage(content="Hello from Gemini", role="assistant")
            yield ResultMessage(error=False, session_id="test-123")

        mock_transport.send_query.side_effect = mock_send_query

        options = GeminiOptions(model="gemini-pro")
        messages = []
        async for msg in client.query("Test prompt", options):
            messages.append(msg)

        assert len(messages) == 1
        assert isinstance(messages[0], Message)
        assert len(messages[0].content) == 1
        assert messages[0].content[0].text == "Hello from Gemini"
        assert messages[0].role == MessageRole.ASSISTANT

        mock_transport.connect.assert_called_once()
        mock_transport.disconnect.assert_called_once()
        mock_transport.send_query.assert_called_once_with("Test prompt", options)

    @pytest.mark.asyncio
    async def test_query_no_options(self, client, mock_transport):
        """Test query with no options (defaults)."""
        client.transport = mock_transport

        async def mock_send_query(prompt, options):
            # Verify default options
            assert isinstance(options, GeminiOptions)
            assert options.auto_approve is True
            assert options.yes_mode is True
            yield GeminiMessage(content="Response")

        mock_transport.send_query.side_effect = mock_send_query

        messages = []
        async for msg in client.query("Test"):
            messages.append(msg)

        assert len(messages) == 1
        assert len(messages[0].content) == 1
        assert messages[0].content[0].text == "Response"

    @pytest.mark.asyncio
    async def test_query_with_error_result(self, client, mock_transport):
        """Test query handling error results."""
        client.transport = mock_transport

        async def mock_send_query(prompt, options):
            yield ResultMessage(error=True, message="API quota exceeded", session_id="test")

        mock_transport.send_query.side_effect = mock_send_query

        with pytest.raises(Exception) as exc_info:
            async for _ in client.query("Test"):
                pass

        assert "API quota exceeded" in str(exc_info.value)
        mock_transport.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_multiple_messages(self, client, mock_transport):
        """Test query with multiple messages."""
        client.transport = mock_transport

        async def mock_send_query(prompt, options):
            yield GeminiMessage(content="Part 1", role="assistant")
            yield GeminiMessage(content="Part 2", role="assistant")
            yield GeminiMessage(content="Part 3", role="assistant")
            yield ResultMessage(error=False)

        mock_transport.send_query.side_effect = mock_send_query

        messages = []
        async for msg in client.query("Test"):
            messages.append(msg)

        assert len(messages) == 3
        assert all(msg.content.startswith("Part") for msg in messages)
        assert all(msg.role == MessageRole.ASSISTANT for msg in messages)

    @pytest.mark.asyncio
    async def test_query_auto_install_on_cli_missing(self, client):
        """Test auto-install when CLI is missing."""

        # First attempt raises CLI missing error
        async def first_send_query(prompt, options):
            msg = "gemini not found"
            raise FileNotFoundError(msg)

        # Second attempt (after install) succeeds
        async def second_send_query(prompt, options):
            yield GeminiMessage(content="Success after install")

        # Set up transport mocks
        client.transport.connect = AsyncMock()
        client.transport.disconnect = AsyncMock()
        client.transport.send_query = AsyncMock(side_effect=first_send_query)

        # Mock successful install
        with patch("claif_gem.client.install_gemini") as mock_install:
            mock_install.return_value = {"installed": ["gemini"]}

            # Mock the retry transport
            with patch("claif_gem.client.GeminiTransport") as MockTransport:
                retry_transport = MockTransport.return_value
                retry_transport.connect = AsyncMock()
                retry_transport.disconnect = AsyncMock()
                retry_transport.send_query = AsyncMock(side_effect=second_send_query)

                messages = []
                async for msg in client.query("Test"):
                    messages.append(msg)

                assert len(messages) == 1
                assert len(messages[0].content) == 1
                assert messages[0].content[0].text == "Success after install"
                mock_install.assert_called_once()
                retry_transport.connect.assert_called_once()
                retry_transport.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_auto_install_fails(self, client):
        """Test when auto-install fails."""

        # Mock transport to raise CLI missing error
        async def mock_send_query(prompt, options):
            msg = "gemini not found"
            raise OSError(msg)

        client.transport.connect = AsyncMock()
        client.transport.disconnect = AsyncMock()
        client.transport.send_query = AsyncMock(side_effect=mock_send_query)

        # Mock failed install
        with patch("claif_gem.client.install_gemini") as mock_install:
            mock_install.return_value = {
                "installed": [],
                "failed": ["gemini"],
                "message": "Installation failed: no permission",
            }

            with pytest.raises(Exception) as exc_info:
                async for _ in client.query("Test"):
                    pass

            assert "auto-install failed" in str(exc_info.value)
            assert "no permission" in str(exc_info.value)
            mock_install.assert_called_once()
            client.transport.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_non_cli_error(self, client, mock_transport):
        """Test that non-CLI errors are re-raised unchanged."""
        client.transport = mock_transport

        async def mock_send_query(prompt, options):
            msg = "Invalid prompt format"
            raise ValueError(msg)

        mock_transport.send_query.side_effect = mock_send_query

        with pytest.raises(ValueError) as exc_info:
            async for _ in client.query("Test"):
                pass

        assert "Invalid prompt format" in str(exc_info.value)
        mock_transport.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_ensures_disconnect(self, client, mock_transport):
        """Test that disconnect is called even on error."""
        client.transport = mock_transport

        async def mock_send_query(prompt, options):
            msg = "Test error"
            raise Exception(msg)

        mock_transport.send_query.side_effect = mock_send_query

        with pytest.raises(Exception):
            async for _ in client.query("Test"):
                pass

        # Disconnect should still be called
        mock_transport.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_connect_error(self, client, mock_transport):
        """Test error during connect."""
        client.transport = mock_transport
        mock_transport.connect.side_effect = ConnectionError("Cannot connect")

        with pytest.raises(ConnectionError) as exc_info:
            async for _ in client.query("Test"):
                pass

        assert "Cannot connect" in str(exc_info.value)
        # Disconnect should still be attempted
        mock_transport.disconnect.assert_called_once()


class TestModuleLevelFunctions:
    """Test module-level functions."""

    def test_get_client_singleton(self):
        """Test that _get_client returns singleton."""
        # Reset global client
        import claif_gem.client

        claif_gem.client._client = None

        client1 = _get_client()
        client2 = _get_client()

        assert client1 is client2
        assert isinstance(client1, GeminiClient)

    @pytest.mark.asyncio
    async def test_query_function(self):
        """Test the module-level query function."""
        with patch("claif_gem.client._get_client") as mock_get_client:
            mock_client = MagicMock()

            async def mock_query(prompt, options):
                yield Message(role=MessageRole.ASSISTANT, content="Module test")

            mock_client.query = mock_query
            mock_get_client.return_value = mock_client

            messages = []
            async for msg in query("Test prompt"):
                messages.append(msg)

            assert len(messages) == 1
            assert len(messages[0].content) == 1
            assert messages[0].content[0].text == "Module test"
            mock_get_client.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_function_with_options(self):
        """Test module-level query with options."""
        with patch("claif_gem.client._get_client") as mock_get_client:
            mock_client = MagicMock()

            received_options = None

            async def mock_query(prompt, options):
                nonlocal received_options
                received_options = options
                yield Message(role=MessageRole.ASSISTANT, content="Test")

            mock_client.query = mock_query
            mock_get_client.return_value = mock_client

            options = GeminiOptions(model="gemini-pro", temperature=0.5)
            messages = []
            async for msg in query("Test", options):
                messages.append(msg)

            assert received_options is options
            assert received_options.model == "gemini-pro"
            assert received_options.temperature == 0.5
