"""Comprehensive test suite for claif_gem CLI."""

import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from claif.common import Message, MessageRole

from claif_gem.cli import GeminiCLI, main
from claif_gem.types import GeminiOptions


class TestGeminiCLI:
    """Test suite for GeminiCLI class."""

    @pytest.fixture
    def cli(self):
        """Create a CLI instance."""
        return GeminiCLI()

    @pytest.fixture
    def mock_query(self):
        """Mock the query function."""
        with patch("claif_gem.cli.query") as mock:
            yield mock

    @pytest.fixture
    def mock_print(self):
        """Mock print functions."""
        with patch("claif_gem.cli._print") as p:
            with patch("claif_gem.cli._print_error") as pe:
                with patch("claif_gem.cli._print_success") as ps:
                    with patch("claif_gem.cli._print_warning") as pw:
                        yield {"print": p, "error": pe, "success": ps, "warning": pw}

    @pytest.mark.asyncio
    async def test_query_basic(self, cli, mock_query, mock_print):
        """Test basic query functionality."""
        # Mock query response
        async def mock_query_impl(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Gemini response")

        mock_query.side_effect = mock_query_impl

        # Test with basic prompt
        await cli.query("Hello Gemini")

        # Verify query was called
        mock_query.assert_called_once()
        call_args = mock_query.call_args
        assert call_args[0][0] == "Hello Gemini"
        assert isinstance(call_args[1]["options"], GeminiOptions)

        # Verify output
        mock_print["print"].assert_called()

    @pytest.mark.asyncio
    async def test_query_with_all_options(self, cli, mock_query):
        """Test query with all options specified."""
        async def mock_query_impl(prompt, options):
            # Verify options
            assert options.model == "gemini-pro"
            assert options.temperature == 0.7
            assert options.system_prompt == "You are helpful"
            assert options.max_context_length == 4096
            assert options.timeout == 90
            assert options.auto_approve is False
            assert options.yes_mode is False
            assert options.verbose is True
            assert options.no_retry is True
            yield Message(role=MessageRole.ASSISTANT, content="Response")

        mock_query.side_effect = mock_query_impl

        cli._config.verbose = True  # Set verbose mode
        
        await cli.query(
            "Test prompt",
            model="gemini-pro",
            temperature=0.7,
            system="You are helpful",
            auto_approve=False,
            yes_mode=False,
            max_context=4096,
            timeout=90,
            no_retry=True
        )

        mock_query.assert_called_once()

    @pytest.mark.asyncio
    async def test_query_json_format(self, cli, mock_query):
        """Test query with JSON output format."""
        async def mock_query_impl(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Gemini response")

        mock_query.side_effect = mock_query_impl

        # Capture output by mocking _print
        output_data = []
        with patch("claif_gem.cli._print", side_effect=lambda x: output_data.append(x)):
            await cli.query("Test", output_format="json")
        
        # Find JSON output
        json_output = None
        for output in output_data:
            try:
                json_output = json.loads(output)
                break
            except:
                continue

        # Verify JSON output
        assert json_output is not None
        assert json_output["prompt"] == "Test"
        assert json_output["response"] == "Gemini response"
        assert "timestamp" in json_output

    @pytest.mark.asyncio
    async def test_query_with_metrics(self, cli, mock_query, mock_print):
        """Test query with metrics display."""
        async def mock_query_impl(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Response")

        mock_query.side_effect = mock_query_impl

        await cli.query("Test", show_metrics=True)

        # Should print metrics
        calls = [str(call[0][0]) for call in mock_print["print"].call_args_list]
        assert any("Duration:" in call or "duration" in call.lower() for call in calls)

    @pytest.mark.asyncio
    async def test_query_error_handling(self, cli, mock_query, mock_print):
        """Test query error handling."""
        async def mock_query_impl(prompt, options):
            raise Exception("Gemini error")

        mock_query.side_effect = mock_query_impl

        with pytest.raises(SystemExit):
            await cli.query("Test")

        # Should print error message
        mock_print["error"].assert_called()
        call_args = mock_print["error"].call_args
        assert "Gemini error" in str(call_args[0][0])

    @pytest.mark.asyncio
    async def test_query_with_images(self, cli, mock_query):
        """Test query with image paths."""
        async def mock_query_impl(prompt, options):
            # Test that _process_images correctly processes image paths
            assert isinstance(options.images, list)
            assert len(options.images) > 0
            yield Message(role=MessageRole.ASSISTANT, content="Image analyzed")

        mock_query.side_effect = mock_query_impl

        # Mock path exists
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.expanduser") as mock_expand:
                with patch("pathlib.Path.resolve") as mock_resolve:
                    mock_expand.return_value.resolve.return_value = "/resolved/path/image.png"
                    
                    await cli.query("Analyze this", images="/path/to/image.png")

    def test_health_success(self, cli):
        """Test health check when service is healthy."""
        with patch.object(cli, "_health_check", new_callable=AsyncMock) as mock_health:
            mock_health.return_value = True
            
            with patch("claif_gem.cli._print_success") as mock_print_success:
                cli.health()
                mock_print_success.assert_called_with("Gemini service is healthy")

    def test_health_failure(self, cli):
        """Test health check when service is not healthy."""
        with patch.object(cli, "_health_check", new_callable=AsyncMock) as mock_health:
            mock_health.return_value = False
            
            with patch("claif_gem.cli._print_error") as mock_print_error:
                with pytest.raises(SystemExit):
                    cli.health()
                mock_print_error.assert_called_with("Gemini service is not responding")

    def test_models(self, cli):
        """Test models command."""
        with patch("claif_gem.cli._print") as mock_print:
            cli.models()

            # Should print available models
            mock_print.assert_any_call("Available Gemini Models:")
            # Check that models are printed
            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            assert any("gemini-pro" in call for call in calls)
            assert any("gemini-flash" in call for call in calls)

    def test_config_show(self, cli):
        """Test config show action."""
        with patch("claif_gem.cli._print") as mock_print:
            cli.config(action="show")

            # Should print configuration
            mock_print.assert_any_call("Gemini Configuration:")
            # Check that config values are printed
            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            assert any("Environment:" in call for call in calls)

    def test_config_set(self, cli):
        """Test config set action."""
        with patch("claif_gem.cli._print_success") as mock_success:
            with patch("claif_gem.cli._print_warning") as mock_warning:
                cli.config(action="set", model="gemini-pro", timeout=120)

                # Should print success messages
                mock_success.assert_any_call("Set model = gemini-pro")
                mock_success.assert_any_call("Set timeout = 120")
                mock_warning.assert_called()

    def test_install(self, cli):
        """Test install command."""
        with patch("claif_gem.cli.install_gemini") as mock_install:
            mock_install.return_value = {
                "installed": ["gemini"],
                "failed": []
            }

            with patch("claif_gem.cli._print_success") as mock_print_success:
                cli.install()

                mock_install.assert_called_once()
                mock_print_success.assert_any_call("Gemini provider installed successfully!")

    def test_install_failure(self, cli):
        """Test install command failure."""
        with patch("claif_gem.cli.install_gemini") as mock_install:
            mock_install.return_value = {
                "installed": [],
                "failed": ["gemini"],
                "message": "Installation failed: permission denied"
            }

            with patch("claif_gem.cli._print_error") as mock_print_error:
                with pytest.raises(SystemExit):
                    cli.install()
                
                mock_print_error.assert_any_call("Failed to install Gemini provider: Installation failed: permission denied")

    def test_status(self, cli):
        """Test status command."""
        with patch("claif_gem.cli._print_success") as mock_success:
            with patch("claif_gem.cli._print_warning") as mock_warning:
                with patch("pathlib.Path.exists", return_value=True):
                    cli.status()
                    # Should show some status
                    assert mock_success.called or mock_warning.called

    @pytest.mark.asyncio
    async def test_stream(self, cli, mock_query):
        """Test stream command."""
        async def mock_query_impl(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Streamed ")
            yield Message(role=MessageRole.ASSISTANT, content="response")

        mock_query.side_effect = mock_query_impl

        with patch("claif_gem.cli._print") as mock_print:
            await cli.stream("Test streaming")

            # Should print streamed content
            mock_print.assert_called()

    @pytest.mark.asyncio
    async def test_benchmark(self, cli, mock_query):
        """Test benchmark command."""
        async def mock_query_impl(prompt, options):
            yield Message(role=MessageRole.ASSISTANT, content="Benchmark response")

        mock_query.side_effect = mock_query_impl

        with patch("claif_gem.cli._print") as mock_print:
            cli.benchmark(iterations=2)

            # Should print benchmark results
            calls = [str(call[0][0]) for call in mock_print.call_args_list]
            assert any("Benchmarking Gemini" in call for call in calls)
            assert any("Average:" in call for call in calls)

    def test_process_images_local_files(self, cli):
        """Test _process_images with local files."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.expanduser") as mock_expand:
                with patch("pathlib.Path.resolve") as mock_resolve:
                    # Mock path resolution
                    mock_path = Mock()
                    mock_path.resolve.return_value = "/resolved/image.png"
                    mock_expand.return_value = mock_path
                    
                    result = cli._process_images("/home/user/image.png,/data/photo.jpg")
                    
                    assert len(result) == 2
                    assert all(isinstance(p, str) for p in result)

    def test_process_images_urls(self, cli):
        """Test _process_images with URLs."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            with patch("tempfile.NamedTemporaryFile") as mock_tempfile:
                # Mock URL download
                mock_response = Mock()
                mock_response.read.return_value = b"image data"
                mock_urlopen.return_value.__enter__.return_value = mock_response
                
                # Mock temp file
                mock_file = Mock()
                mock_file.name = "/tmp/image123.jpg"
                mock_tempfile.return_value.__enter__.return_value = mock_file
                
                result = cli._process_images("https://example.com/image.jpg")
                
                assert len(result) == 1
                assert result[0] == "/tmp/image123.jpg"


class TestMainFunction:
    """Test main entry point function."""

    def test_main(self):
        """Test main function."""
        with patch("claif_gem.cli.fire.Fire") as mock_fire:
            from claif_gem.cli import main
            main()
            mock_fire.assert_called_once_with(GeminiCLI)

    def test_main_with_args(self):
        """Test main with command line arguments."""
        test_args = ["query", "Hello Gemini", "--model", "gemini-pro"]
        
        with patch("sys.argv", ["claif-gem"] + test_args):
            with patch("claif_gem.cli.fire.Fire") as mock_fire:
                from claif_gem.cli import main
                main()
                mock_fire.assert_called_once_with(GeminiCLI)