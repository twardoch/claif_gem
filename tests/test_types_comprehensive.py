"""Comprehensive test suite for claif_gem types."""

import pytest
from pathlib import Path
from claif.common import Message, MessageRole

from claif_gem.types import GeminiMessage, GeminiOptions, GeminiResponse, ResultMessage


class TestGeminiOptions:
    """Test suite for GeminiOptions dataclass."""

    def test_default_options(self):
        """Test default option values."""
        options = GeminiOptions()
        
        assert options.auto_approve is True
        assert options.yes_mode is True
        assert options.cwd is None
        assert options.system_prompt is None
        assert options.max_context_length is None
        assert options.temperature is None
        assert options.model is None
        assert options.timeout is None
        assert options.verbose is False
        assert options.exec_path is None
        assert options.images is None
        assert options.retry_count == 3
        assert options.retry_delay == 1.0
        assert options.no_retry is False

    def test_custom_options(self):
        """Test custom option values."""
        options = GeminiOptions(
            auto_approve=False,
            yes_mode=False,
            cwd="/tmp/work",
            system_prompt="You are a helpful assistant",
            max_context_length=8192,
            temperature=0.9,
            model="gemini-pro",
            timeout=120,
            verbose=True,
            exec_path="/custom/path/gemini",
            images=["/img1.png", "/img2.jpg"],
            retry_count=5,
            retry_delay=2.0,
            no_retry=True
        )
        
        assert options.auto_approve is False
        assert options.yes_mode is False
        assert options.cwd == "/tmp/work"
        assert options.system_prompt == "You are a helpful assistant"
        assert options.max_context_length == 8192
        assert options.temperature == 0.9
        assert options.model == "gemini-pro"
        assert options.timeout == 120
        assert options.verbose is True
        assert options.exec_path == "/custom/path/gemini"
        assert options.images == ["/img1.png", "/img2.jpg"]
        assert options.retry_count == 5
        assert options.retry_delay == 2.0
        assert options.no_retry is True

    def test_cwd_with_path_object(self):
        """Test cwd can accept Path objects."""
        path = Path("/home/user/project")
        options = GeminiOptions(cwd=path)
        assert options.cwd == path

    def test_partial_options(self):
        """Test creating options with only some values specified."""
        options = GeminiOptions(
            model="gemini-flash",
            temperature=0.5,
            verbose=True
        )
        
        # Specified values
        assert options.model == "gemini-flash"
        assert options.temperature == 0.5
        assert options.verbose is True
        
        # Defaults for unspecified
        assert options.auto_approve is True
        assert options.yes_mode is True
        assert options.retry_count == 3


class TestGeminiMessage:
    """Test suite for GeminiMessage class."""

    def test_message_creation_defaults(self):
        """Test basic message creation with defaults."""
        msg = GeminiMessage(content="Hello world")
        assert msg.content == "Hello world"
        assert msg.role == "assistant"

    def test_message_creation_custom_role(self):
        """Test message creation with custom role."""
        msg = GeminiMessage(content="User input", role="user")
        assert msg.content == "User input"
        assert msg.role == "user"

    def test_to_claif_message_assistant(self):
        """Test conversion to Claif message with assistant role."""
        msg = GeminiMessage(content="Assistant response", role="assistant")
        claif_msg = msg.to_claif_message()
        
        assert isinstance(claif_msg, Message)
        assert claif_msg.role == MessageRole.ASSISTANT
        assert claif_msg.content == "Assistant response"

    def test_to_claif_message_user(self):
        """Test conversion to Claif message with user role."""
        msg = GeminiMessage(content="User query", role="user")
        claif_msg = msg.to_claif_message()
        
        assert isinstance(claif_msg, Message)
        assert claif_msg.role == MessageRole.USER
        assert claif_msg.content == "User query"

    def test_to_claif_message_unknown_role(self):
        """Test conversion with unknown role defaults to user."""
        msg = GeminiMessage(content="System message", role="system")
        claif_msg = msg.to_claif_message()
        
        # Unknown roles should map to USER
        assert claif_msg.role == MessageRole.USER
        assert claif_msg.content == "System message"

    def test_empty_content(self):
        """Test message with empty content."""
        msg = GeminiMessage(content="")
        assert msg.content == ""
        
        claif_msg = msg.to_claif_message()
        assert claif_msg.content == ""


class TestGeminiResponse:
    """Test suite for GeminiResponse class."""

    def test_response_creation_minimal(self):
        """Test minimal response creation."""
        response = GeminiResponse(content="Response text")
        
        assert response.content == "Response text"
        assert response.role == "assistant"
        assert response.model is None
        assert response.usage is None
        assert response.raw_response is None

    def test_response_creation_full(self):
        """Test full response creation with all fields."""
        usage_data = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        raw_data = {"id": "123", "object": "chat.completion", "created": 1234567890}
        
        response = GeminiResponse(
            content="Full response",
            role="assistant",
            model="gemini-pro",
            usage=usage_data,
            raw_response=raw_data
        )
        
        assert response.content == "Full response"
        assert response.role == "assistant"
        assert response.model == "gemini-pro"
        assert response.usage == usage_data
        assert response.raw_response == raw_data

    def test_to_claif_message_assistant(self):
        """Test conversion to Claif message with assistant role."""
        response = GeminiResponse(
            content="Assistant text",
            role="assistant",
            model="gemini-pro"
        )
        
        claif_msg = response.to_claif_message()
        assert isinstance(claif_msg, Message)
        assert claif_msg.role == MessageRole.ASSISTANT
        assert claif_msg.content == "Assistant text"

    def test_to_claif_message_user(self):
        """Test conversion to Claif message with user role."""
        response = GeminiResponse(
            content="User text",
            role="user"
        )
        
        claif_msg = response.to_claif_message()
        assert claif_msg.role == MessageRole.USER
        assert claif_msg.content == "User text"

    def test_to_claif_message_preserves_content_only(self):
        """Test that conversion only preserves content and role, not metadata."""
        response = GeminiResponse(
            content="Content only",
            role="assistant",
            model="gemini-pro",
            usage={"tokens": 100},
            raw_response={"extra": "data"}
        )
        
        claif_msg = response.to_claif_message()
        # The Message object should only have role and content
        assert claif_msg.role == MessageRole.ASSISTANT
        assert claif_msg.content == "Content only"
        # Verify it's a simple Message, not containing the extra metadata
        assert not hasattr(claif_msg, "model")
        assert not hasattr(claif_msg, "usage")


class TestResultMessage:
    """Test suite for ResultMessage class."""

    def test_result_message_defaults(self):
        """Test default values for ResultMessage."""
        msg = ResultMessage()
        
        assert msg.type == "result"
        assert msg.duration is None
        assert msg.error is False
        assert msg.message is None
        assert msg.session_id is None

    def test_result_message_success(self):
        """Test successful result message."""
        msg = ResultMessage(
            duration=1.23,
            error=False,
            message="Query completed successfully",
            session_id="abc-123"
        )
        
        assert msg.type == "result"
        assert msg.duration == 1.23
        assert msg.error is False
        assert msg.message == "Query completed successfully"
        assert msg.session_id == "abc-123"

    def test_result_message_error(self):
        """Test error result message."""
        msg = ResultMessage(
            duration=0.5,
            error=True,
            message="API rate limit exceeded",
            session_id="xyz-789"
        )
        
        assert msg.type == "result"
        assert msg.duration == 0.5
        assert msg.error is True
        assert msg.message == "API rate limit exceeded"
        assert msg.session_id == "xyz-789"

    def test_result_message_minimal_error(self):
        """Test minimal error result."""
        msg = ResultMessage(error=True)
        
        assert msg.error is True
        assert msg.duration is None
        assert msg.message is None

    def test_result_message_type_immutable(self):
        """Test that type field has correct default."""
        msg1 = ResultMessage()
        msg2 = ResultMessage(type="result")
        msg3 = ResultMessage(type="custom")  # Should be allowed but not recommended
        
        assert msg1.type == "result"
        assert msg2.type == "result"
        assert msg3.type == "custom"