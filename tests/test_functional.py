# this_file: claif_gem/tests/test_functional.py
"""Functional tests for claif_gem that validate actual client behavior."""

import json
from unittest.mock import MagicMock, patch

import pytest
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice
from openai.types.chat.chat_completion_chunk import Choice as ChunkChoice
from openai.types.chat.chat_completion_chunk import ChoiceDelta
from openai.types.chat.chat_completion_message import ChatCompletionMessage
from openai.types.completion_usage import CompletionUsage

from claif_gem.client import GeminiClient


class TestGeminiClientFunctional:
    """Functional tests for the GeminiClient."""

    @pytest.fixture
    def mock_gemini_response(self):
        """Create a mock response from Gemini CLI."""
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Hello! I'm Gemini, Google's AI assistant. How can I help you today?"}],
                        "role": "model",
                    },
                    "finishReason": "STOP",
                    "index": 0,
                }
            ],
            "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 15, "totalTokenCount": 25},
        }

    @patch("claif_gem.client.subprocess.run")
    @patch("shutil.which")
    def test_basic_query(self, mock_which, mock_run, mock_gemini_response):
        """Test basic non-streaming query functionality."""
        # Setup mocks
        mock_which.return_value = "/usr/local/bin/gemini"
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_gemini_response), stderr="")

        # Create client
        client = GeminiClient()

        # Execute
        response = client.chat.completions.create(
            model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello Gemini"}]
        )

        # Verify response structure
        assert isinstance(response, ChatCompletion)
        # The implementation parses JSON, so we should get the extracted text
        expected_content = "Hello! I'm Gemini, Google's AI assistant. How can I help you today?"
        # Since the mock returns the full JSON, the implementation will extract it
        assert expected_content in response.choices[0].message.content
        assert response.choices[0].message.role == "assistant"
        assert response.model == "gemini-1.5-flash"

        # Verify subprocess was called correctly
        mock_run.assert_called_once()
        call_args = mock_run.call_args

        # Check command structure
        cmd = call_args[0][0]
        assert "gemini" in cmd[0]
        assert "-y" in cmd
        assert "--model" in cmd
        assert "gemini-1.5-flash" in cmd[cmd.index("--model") + 1]
        # Prompt should be the last argument
        assert "Hello Gemini" in cmd[-1]

    @patch("claif_gem.client.subprocess.Popen")
    @patch("shutil.which")
    def test_streaming_query(self, mock_which, mock_popen):
        """Test streaming query functionality."""
        # Setup mocks
        mock_which.return_value = "/usr/local/bin/gemini"

        # Mock process with streaming output
        mock_process = MagicMock()
        mock_process.poll.side_effect = [None, None, None, 0]  # Process runs then completes
        mock_process.returncode = 0

        # Simulate streaming JSON responses
        streaming_responses = [
            json.dumps({"candidates": [{"content": {"parts": [{"text": "Hello"}]}}]}) + "\n",
            json.dumps({"candidates": [{"content": {"parts": [{"text": " from"}]}}]}) + "\n",
            json.dumps({"candidates": [{"content": {"parts": [{"text": " Gemini!"}]}}]}) + "\n",
            "",  # EOF
        ]
        mock_process.stdout.readline.side_effect = streaming_responses
        mock_process.stderr.read.return_value = ""

        mock_popen.return_value = mock_process

        client = GeminiClient()

        # Note: The current implementation doesn't have real streaming
        # It falls back to sync mode, so we test that
        with patch("claif_gem.client.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="Hello from Gemini!", stderr="")

            # Execute with streaming
            stream = client.chat.completions.create(
                model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello"}], stream=True
            )

            # Collect chunks
            chunks = list(stream)

            # Verify we got chunks
            assert len(chunks) >= 3
            assert all(isinstance(chunk, ChatCompletionChunk) for chunk in chunks)

            # Verify content
            content_parts = []
            for chunk in chunks:
                if chunk.choices and chunk.choices[0].delta.content:
                    content_parts.append(chunk.choices[0].delta.content)

            assert "Hello from Gemini!" in "".join(content_parts)

    @patch("claif_gem.client.subprocess.run")
    @patch("shutil.which")
    def test_with_parameters(self, mock_which, mock_run, mock_gemini_response):
        """Test query with additional parameters."""
        # Setup mocks
        mock_which.return_value = "/usr/local/bin/gemini"
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_gemini_response), stderr="")

        client = GeminiClient()

        # Execute with parameters
        client.chat.completions.create(
            model="gemini-1.5-pro",
            messages=[
                {"role": "system", "content": "You are a helpful coding assistant."},
                {"role": "user", "content": "Write a hello world function"},
            ],
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
        )

        # Verify subprocess was called with parameters
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        cmd = call_args[0][0]

        # Check parameters in command
        assert "--temperature" in cmd
        assert "0.7" in cmd
        assert "--max-output-tokens" in cmd
        assert "100" in cmd
        assert "--model" in cmd
        assert "gemini-1.5-pro" in cmd[cmd.index("--model") + 1]
        # Prompt should include system message
        assert "You are a helpful coding assistant" in cmd[-1]

    @patch("claif_gem.client.subprocess.run")
    @patch("shutil.which")
    def test_error_handling(self, mock_which, mock_run):
        """Test error handling for CLI failures."""
        # Setup mocks
        mock_which.return_value = "/usr/local/bin/gemini"
        # Make subprocess.run raise CalledProcessError
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(
            returncode=1, cmd=["/usr/local/bin/gemini"], stderr="Error: API quota exceeded"
        )

        client = GeminiClient()

        # Execute and verify error
        with pytest.raises(RuntimeError) as exc_info:
            client.chat.completions.create(model="gemini-1.5-flash", messages=[{"role": "user", "content": "Hello"}])

        assert "Gemini CLI error" in str(exc_info.value)
        assert "API quota exceeded" in str(exc_info.value)

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_file")
    def test_cli_not_found(self, mock_is_file, mock_exists, mock_which):
        """Test error when Gemini CLI is not found."""
        mock_which.return_value = None
        mock_exists.return_value = False
        mock_is_file.return_value = False

        # Should raise error during initialization
        with pytest.raises(FileNotFoundError) as exc_info:
            GeminiClient()

        assert "Gemini CLI not found" in str(exc_info.value)

    @patch("claif_gem.client.subprocess.run")
    @patch("shutil.which")
    def test_model_name_mapping(self, mock_which, mock_run, mock_gemini_response):
        """Test that OpenAI model names are mapped to Gemini names."""
        # Setup mocks
        mock_which.return_value = "/usr/local/bin/gemini"
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_gemini_response), stderr="")

        client = GeminiClient()

        # Test with OpenAI model name
        client.chat.completions.create(
            model="gpt-3.5-turbo",  # Should map to gemini-1.5-flash
            messages=[{"role": "user", "content": "Hello"}],
        )

        # Verify mapping worked
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        model_idx = cmd.index("--model") + 1
        assert "gemini-1.5-flash" in cmd[model_idx]

    @patch("claif_gem.client.subprocess.run")
    @patch("shutil.which")
    def test_multi_turn_conversation(self, mock_which, mock_run, mock_gemini_response):
        """Test multi-turn conversation handling."""
        # Setup mocks
        mock_which.return_value = "/usr/local/bin/gemini"
        mock_run.return_value = MagicMock(returncode=0, stdout=json.dumps(mock_gemini_response), stderr="")

        client = GeminiClient()

        # Execute with conversation history
        client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=[
                {"role": "user", "content": "Hi, my name is Alice"},
                {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
                {"role": "user", "content": "What's my name?"},
            ],
        )

        # Verify the conversation was formatted in the prompt
        call_args = mock_run.call_args
        cmd = call_args[0][0]
        # Prompt is the last argument
        prompt = cmd[-1]

        # Should contain conversation context
        assert "Alice" in prompt
        assert "What's my name?" in prompt


class TestGeminiClientIntegration:
    """Integration tests that would run against real Gemini CLI."""

    @pytest.mark.skip(reason="Requires Gemini CLI and API key")
    def test_real_gemini_connection(self):
        """Test connection to real Gemini API."""
        client = GeminiClient()

        try:
            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[{"role": "user", "content": "Say 'test successful' and nothing else"}],
                max_tokens=10,
            )

            assert "test successful" in response.choices[0].message.content.lower()
        except Exception as e:
            pytest.skip(f"Gemini CLI not available: {e}")

    @pytest.mark.skip(reason="Requires Gemini CLI and API key")
    def test_real_streaming(self):
        """Test streaming with real Gemini CLI."""
        client = GeminiClient()

        try:
            stream = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[{"role": "user", "content": "Count to 3"}],
                stream=True,
                max_tokens=20,
            )

            chunks = list(stream)
            assert len(chunks) > 0

            # Reconstruct message
            full_content = "".join(
                chunk.choices[0].delta.content or ""
                for chunk in chunks
                if chunk.choices and chunk.choices[0].delta.content
            )

            # Should contain numbers
            assert any(num in full_content for num in ["1", "2", "3"])
        except Exception as e:
            pytest.skip(f"Gemini CLI not available: {e}")
