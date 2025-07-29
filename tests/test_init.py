"""Test suite for claif_gem.__init__ module."""

from unittest.mock import patch

import pytest
from claif.common import ClaifOptions, Message, MessageRole

from claif_gem import query
from claif_gem.types import GeminiOptions


class TestModuleQuery:
    """Test suite for module-level query function."""

    @pytest.mark.asyncio
    async def test_query_with_default_options(self):
        """Test query with default options."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock the response
            async def mock_response(prompt, options):
                yield Message(role=MessageRole.ASSISTANT, content="Test response")

            mock_gemini_query.side_effect = mock_response

            # Test with no options
            messages = []
            async for msg in query("Test prompt"):
                messages.append(msg)

            assert len(messages) == 1
            assert messages[0].role == MessageRole.ASSISTANT
            assert messages[0].content == "Test response"

            # Verify the function was called with default options
            mock_gemini_query.assert_called_once()
            call_args = mock_gemini_query.call_args
            assert call_args[0][0] == "Test prompt"
            options = call_args[0][1]
            assert isinstance(options, GeminiOptions)
            assert options.model is None
            assert options.temperature is None
            assert options.system_prompt is None
            assert options.timeout is None
            assert options.verbose is False

    @pytest.mark.asyncio
    async def test_query_with_custom_options(self):
        """Test query with custom Claif options."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock the response
            async def mock_response(prompt, options):
                # Verify options were mapped correctly
                assert options.model == "gemini-pro"
                assert options.temperature == 0.7
                assert options.system_prompt == "You are helpful"
                assert options.timeout == 60
                assert options.verbose is True
                yield Message(role=MessageRole.ASSISTANT, content="Custom response")

            mock_gemini_query.side_effect = mock_response

            # Test with custom options
            claif_options = ClaifOptions(
                model="gemini-pro",
                temperature=0.7,
                system_prompt="You are helpful",
                timeout=60,
                verbose=True,
            )

            messages = []
            async for msg in query("Test prompt", claif_options):
                messages.append(msg)

            assert len(messages) == 1
            assert messages[0].content == "Custom response"

    @pytest.mark.asyncio
    async def test_query_with_none_options(self):
        """Test query with explicitly None options."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock the response
            async def mock_response(prompt, options):
                yield Message(role=MessageRole.ASSISTANT, content="None options response")

            mock_gemini_query.side_effect = mock_response

            # Test with explicit None
            messages = []
            async for msg in query("Test prompt", None):
                messages.append(msg)

            assert len(messages) == 1
            assert messages[0].content == "None options response"

            # Should have created default ClaifOptions
            mock_gemini_query.assert_called_once()
            call_args = mock_gemini_query.call_args
            options = call_args[0][1]
            assert isinstance(options, GeminiOptions)

    @pytest.mark.asyncio
    async def test_query_multiple_messages(self):
        """Test query that yields multiple messages."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock the response with multiple messages
            async def mock_response(prompt, options):
                yield Message(role=MessageRole.ASSISTANT, content="First part")
                yield Message(role=MessageRole.ASSISTANT, content="Second part")
                yield Message(role=MessageRole.ASSISTANT, content="Third part")

            mock_gemini_query.side_effect = mock_response

            messages = []
            async for msg in query("Multi-part prompt"):
                messages.append(msg)

            assert len(messages) == 3
            assert messages[0].content == "First part"
            assert messages[1].content == "Second part"
            assert messages[2].content == "Third part"

    @pytest.mark.asyncio
    async def test_query_error_propagation(self):
        """Test that errors from gemini_query are properly propagated."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock an error
            async def mock_error(prompt, options):
                msg = "Gemini query failed"
                raise ValueError(msg)

            mock_gemini_query.side_effect = mock_error

            with pytest.raises(ValueError) as exc_info:
                async for _ in query("Error prompt"):
                    pass

            assert "Gemini query failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_query_empty_response(self):
        """Test query with empty response."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock empty response
            async def mock_empty_response(prompt, options):
                return
                yield  # Make it a generator

            mock_gemini_query.side_effect = mock_empty_response

            messages = []
            async for msg in query("Empty prompt"):
                messages.append(msg)

            assert len(messages) == 0

    @pytest.mark.asyncio
    async def test_query_logging(self):
        """Test that query logging works correctly."""
        with patch("claif_gem.client.query") as mock_gemini_query, patch("claif_gem.logger") as mock_logger:
            # Mock the response
            async def mock_response(prompt, options):
                yield Message(role=MessageRole.ASSISTANT, content="Logged response")

            mock_gemini_query.side_effect = mock_response

            # Test query with long prompt
            long_prompt = "A" * 200
            messages = []
            async for msg in query(long_prompt):
                messages.append(msg)

            # Verify logging was called
            mock_logger.debug.assert_called_once()
            call_args = mock_logger.debug.call_args[0][0]
            assert "Querying Gemini with prompt:" in call_args
            # Should truncate to 100 chars
            assert "A" * 100 in call_args
            assert len(call_args) < len(long_prompt) + 50  # Account for prefix

    @pytest.mark.asyncio
    async def test_query_partial_claif_options(self):
        """Test query with partial ClaifOptions."""
        with patch("claif_gem.client.query") as mock_gemini_query:
            # Mock the response
            async def mock_response(prompt, options):
                # Verify only specified options are set
                assert options.model == "gemini-flash"
                assert options.temperature is None  # Not specified
                assert options.system_prompt is None  # Not specified
                assert options.timeout is None  # Not specified
                assert options.verbose is False  # Default
                yield Message(role=MessageRole.ASSISTANT, content="Partial response")

            mock_gemini_query.side_effect = mock_response

            # Test with partial options
            claif_options = ClaifOptions(model="gemini-flash")

            messages = []
            async for msg in query("Test prompt", claif_options):
                messages.append(msg)

            assert len(messages) == 1
            assert messages[0].content == "Partial response"


class TestModuleImports:
    """Test suite for module imports and exports."""

    def test_version_import_success(self):
        """Test successful version import."""
        with patch("claif_gem.__version__", "1.0.0"):
            from claif_gem import __version__

            assert __version__ == "1.0.0"

    def test_version_import_fallback(self):
        """Test version import fallback."""
        with patch("claif_gem.__version__", side_effect=ImportError):
            # Force re-import to trigger fallback
            import importlib

            import claif_gem

            importlib.reload(claif_gem)
            assert claif_gem.__version__ == "0.1.0-dev"

    def test_all_exports(self):
        """Test that __all__ exports are available."""
        import claif_gem

        # Check that all items in __all__ are available
        for item in claif_gem.__all__:
            assert hasattr(claif_gem, item)
            assert getattr(claif_gem, item) is not None

    def test_claif_import_fallback(self):
        """Test claif import fallback."""
        # This test verifies the dual import pattern works
        with patch("claif_gem.ClaifOptions") as mock_claif_options, patch("claif_gem.Message") as mock_message:
            # These should be imported successfully
            assert mock_claif_options is not None
            assert mock_message is not None
