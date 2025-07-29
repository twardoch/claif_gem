# this_file: claif_gem/tests/test_openai_client.py
"""Tests for Gemini client with OpenAI compatibility."""

import unittest
from unittest.mock import MagicMock, patch

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
)

from claif_gem.client import GeminiClient


class TestGeminiClient(unittest.TestCase):
    """Test cases for GeminiClient."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = GeminiClient(api_key="test-key")

    @patch.dict("os.environ", {}, clear=True)
    def test_init_default(self):
        """Test client initialization with defaults."""
        client = GeminiClient()
        assert client.api_key is None  # No key if not in env
        assert not client.use_vertex_ai
        assert client.timeout == 600.0
        assert client._client is None  # Client should be None when no API key

    def test_init_custom(self):
        """Test client initialization with custom values."""
        client = GeminiClient(
            api_key="test-key", project="test-project", location="us-west1", timeout=300.0, use_vertex_ai=True
        )
        assert client.api_key is None  # api_key is None when using Vertex AI
        assert client.project == "test-project"
        assert client.location == "us-west1"
        assert client.timeout == 300.0
        assert client.use_vertex_ai

    @patch.dict("os.environ", {"GEMINI_API_KEY": "env-key"})
    def test_init_from_env(self):
        """Test client initialization from environment variables."""
        client = GeminiClient()
        assert client.api_key == "env-key"

    @patch.dict("os.environ", {"GOOGLE_API_KEY": "google-env-key"})
    def test_init_from_google_env(self):
        """Test client initialization from Google API key env var."""
        client = GeminiClient()
        assert client.api_key == "google-env-key"

    @patch.dict("os.environ", {"GOOGLE_GENAI_USE_VERTEXAI": "true", "GOOGLE_CLOUD_PROJECT": "my-project"})
    def test_init_vertex_from_env(self):
        """Test Vertex AI initialization from environment variables."""
        client = GeminiClient()
        assert client.use_vertex_ai
        assert client.project == "my-project"

    def test_namespace_structure(self):
        """Test that the client has the correct namespace structure."""
        assert self.client.chat is not None
        assert self.client.chat.completions is not None
        assert hasattr(self.client.chat.completions, "create")

    @patch("google.genai.Client")
    def test_create_sync(self, mock_genai_client_class):
        """Test synchronous chat completion creation."""
        # Mock the GenAI client
        mock_genai_client = MagicMock()
        mock_genai_client_class.return_value = mock_genai_client

        # Mock chat session
        mock_chat = MagicMock()
        mock_genai_client.chats.create.return_value = mock_chat

        # Mock response
        mock_response = MagicMock()
        mock_response.text = "Hello from Gemini!"
        mock_response.usage_metadata.prompt_token_count = 10
        mock_response.usage_metadata.candidates_token_count = 5
        mock_chat.send_message.return_value = mock_response

        # Create client and make request
        client = GeminiClient()
        response = client.chat.completions.create(
            model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello"}]
        )

        # Verify response
        assert isinstance(response, ChatCompletion)
        assert response.model == "gemini-1.5-flash"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "Hello from Gemini!"
        assert response.choices[0].message.role == "assistant"
        assert response.usage.total_tokens == 15

    @patch("google.genai.Client")
    def test_create_stream(self, mock_genai_client_class):
        """Test streaming chat completion creation."""
        # Mock the GenAI client
        mock_genai_client = MagicMock()
        mock_genai_client_class.return_value = mock_genai_client

        # Mock chat session
        mock_chat = MagicMock()
        mock_genai_client.chats.create.return_value = mock_chat

        # Mock streaming response
        mock_chunks = [
            MagicMock(text="Hello"),
            MagicMock(text=" from Gemini!"),
        ]
        mock_chat.send_message.return_value = iter(mock_chunks)

        # Create client and make streaming request
        client = GeminiClient()
        stream = client.chat.completions.create(
            model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello"}], stream=True
        )

        # Collect chunks
        chunks = list(stream)

        # Verify chunks
        assert len(chunks) == 4  # Role chunk + 2 content chunks + finish chunk
        assert isinstance(chunks[0], ChatCompletionChunk)
        assert chunks[0].choices[0].delta.role == "assistant"
        assert chunks[1].choices[0].delta.content == "Hello"
        assert chunks[2].choices[0].delta.content == " from Gemini!"
        assert chunks[3].choices[0].finish_reason == "stop"

    @patch("google.genai.Client")
    def test_message_conversion(self, mock_genai_client_class):
        """Test that messages are correctly converted to Gemini format."""
        # Mock the GenAI client
        mock_genai_client = MagicMock()
        mock_genai_client_class.return_value = mock_genai_client

        # Mock chat session
        mock_chat = MagicMock()
        mock_genai_client.chats.create.return_value = mock_chat
        mock_chat.send_message.return_value = MagicMock(text="Response")

        # Create client and make request with various message types
        client = GeminiClient()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"},
            {"role": "user", "content": "How are you?"},
        ]

        client.chat.completions.create(model="gemini-1.5-flash", messages=messages)

        # Verify the chat was created with system instruction
        mock_genai_client.chats.create.assert_called_once()
        call_args = mock_genai_client.chats.create.call_args[1]

        assert call_args["model"] == "gemini-1.5-flash"
        assert call_args["system_instruction"] == "You are helpful"

        # Verify messages were sent correctly (excluding system)
        assert mock_chat.send_message.call_count == 3

    def test_model_name_mapping(self):
        """Test model name mapping from OpenAI to Gemini."""
        namespace = self.client.chat.completions

        assert namespace._map_model_name("gpt-4") == "gemini-1.5-pro"
        assert namespace._map_model_name("gpt-3.5-turbo") == "gemini-1.5-flash"
        assert namespace._map_model_name("gemini-pro") == "gemini-1.5-pro"
        assert namespace._map_model_name("custom-model") == "custom-model"

    def test_finish_reason_mapping(self):
        """Test finish reason mapping from Gemini to OpenAI."""
        namespace = self.client.chat.completions

        assert namespace._map_finish_reason("STOP") == "stop"
        assert namespace._map_finish_reason("MAX_TOKENS") == "length"
        assert namespace._map_finish_reason("SAFETY") == "content_filter"
        assert namespace._map_finish_reason(None) == "stop"

    def test_backward_compatibility(self):
        """Test the backward compatibility create method."""
        with patch.object(self.client.chat.completions, "create") as mock_create:
            mock_create.return_value = MagicMock(spec=ChatCompletion)

            self.client.create(model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello"}])

            mock_create.assert_called_once_with(
                model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello"}]
            )


if __name__ == "__main__":
    unittest.main()
