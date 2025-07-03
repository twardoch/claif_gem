"""Comprehensive test suite for claif_gem installation functionality."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from claif_gem.install import (
    get_gemini_status,
    install_gemini,
    install_gemini_bundled,
    is_gemini_installed,
    uninstall_gemini,
)


class TestInstallGeminiBundled:
    """Test suite for install_gemini_bundled function."""

    def test_install_success(self):
        """Test successful bundled installation."""
        install_dir = Path("/tmp/claif/bin")
        dist_dir = Path("/tmp/dist")
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("claif_gem.install.shutil.copy2") as mock_copy:
                with patch("pathlib.Path.chmod") as mock_chmod:
                    result = install_gemini_bundled(install_dir, dist_dir)
                    
                    assert result is True
                    mock_copy.assert_called_once()
                    source, target = mock_copy.call_args[0]
                    assert str(source) == str(dist_dir / "gemini" / "gemini")
                    assert str(target) == str(install_dir / "gemini")
                    mock_chmod.assert_called_once_with(0o755)

    def test_install_source_not_found(self):
        """Test when bundled source doesn't exist."""
        install_dir = Path("/tmp/claif/bin")
        dist_dir = Path("/tmp/dist")
        
        with patch("pathlib.Path.exists", return_value=False):
            result = install_gemini_bundled(install_dir, dist_dir)
            assert result is False

    def test_install_copy_exception(self):
        """Test when copy operation fails."""
        install_dir = Path("/tmp/claif/bin")
        dist_dir = Path("/tmp/dist")
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("claif_gem.install.shutil.copy2", side_effect=OSError("Permission denied")):
                result = install_gemini_bundled(install_dir, dist_dir)
                assert result is False


class TestInstallGemini:
    """Test suite for install_gemini function."""

    @patch("claif_gem.install.ensure_bun_installed")
    def test_install_bun_failure(self, mock_ensure_bun):
        """Test install when bun installation fails."""
        mock_ensure_bun.return_value = False
        
        result = install_gemini()
        
        assert result["installed"] == []
        assert result["failed"] == ["gemini"]
        assert result["message"] == "bun installation failed"

    @patch("claif_gem.install.ensure_bun_installed")
    @patch("claif_gem.install.get_install_location")
    @patch("claif_gem.install.install_npm_package_globally")
    def test_install_npm_failure(self, mock_npm_install, mock_get_location, mock_ensure_bun):
        """Test install when npm package installation fails."""
        mock_ensure_bun.return_value = True
        mock_get_location.return_value = Path("/tmp/claif/bin")
        mock_npm_install.return_value = False
        
        result = install_gemini()
        
        assert result["installed"] == []
        assert result["failed"] == ["gemini"]
        assert result["message"] == "@google-ai/gemini-cli installation failed"
        mock_npm_install.assert_called_once_with("@google-ai/gemini-cli")

    @patch("claif_gem.install.ensure_bun_installed")
    @patch("claif_gem.install.get_install_location")
    @patch("claif_gem.install.install_npm_package_globally")
    @patch("claif_gem.install.bundle_all_tools")
    def test_install_bundle_failure(self, mock_bundle, mock_npm_install, mock_get_location, mock_ensure_bun):
        """Test install when bundling fails."""
        mock_ensure_bun.return_value = True
        mock_get_location.return_value = Path("/tmp/claif/bin")
        mock_npm_install.return_value = True
        mock_bundle.return_value = None  # Bundling failed
        
        result = install_gemini()
        
        assert result["installed"] == []
        assert result["failed"] == ["gemini"]
        assert result["message"] == "bundling failed"

    @patch("claif_gem.install.ensure_bun_installed")
    @patch("claif_gem.install.get_install_location")
    @patch("claif_gem.install.install_npm_package_globally")
    @patch("claif_gem.install.bundle_all_tools")
    @patch("claif_gem.install.install_gemini_bundled")
    @patch("claif_gem.install.prompt_tool_configuration")
    def test_install_success(self, mock_prompt, mock_install_bundled, mock_bundle, 
                           mock_npm_install, mock_get_location, mock_ensure_bun):
        """Test successful installation."""
        mock_ensure_bun.return_value = True
        mock_get_location.return_value = Path("/tmp/claif/bin")
        mock_npm_install.return_value = True
        mock_bundle.return_value = Path("/tmp/dist")
        mock_install_bundled.return_value = True
        
        result = install_gemini()
        
        assert result["installed"] == ["gemini"]
        assert result["failed"] == []
        
        # Verify calls
        mock_npm_install.assert_called_once_with("@google-ai/gemini-cli")
        mock_bundle.assert_called_once()
        mock_install_bundled.assert_called_once_with(
            Path("/tmp/claif/bin"),
            Path("/tmp/dist")
        )
        mock_prompt.assert_called_once_with(
            "Gemini",
            [
                "gemini auth login",
                "gemini config set --api-key YOUR_API_KEY",
                "gemini --help",
            ]
        )

    @patch("claif_gem.install.ensure_bun_installed")
    @patch("claif_gem.install.get_install_location")
    @patch("claif_gem.install.install_npm_package_globally")
    @patch("claif_gem.install.bundle_all_tools")
    @patch("claif_gem.install.install_gemini_bundled")
    def test_install_bundled_failure(self, mock_install_bundled, mock_bundle, 
                                   mock_npm_install, mock_get_location, mock_ensure_bun):
        """Test when bundled installation fails."""
        mock_ensure_bun.return_value = True
        mock_get_location.return_value = Path("/tmp/claif/bin")
        mock_npm_install.return_value = True
        mock_bundle.return_value = Path("/tmp/dist")
        mock_install_bundled.return_value = False
        
        result = install_gemini()
        
        assert result["installed"] == []
        assert result["failed"] == ["gemini"]
        assert result["message"] == "gemini installation failed"


class TestUninstallGemini:
    """Test suite for uninstall_gemini function."""

    @patch("claif_gem.install.uninstall_tool")
    def test_uninstall_success(self, mock_uninstall):
        """Test successful uninstallation."""
        mock_uninstall.return_value = True
        
        result = uninstall_gemini()
        
        assert result["uninstalled"] == ["gemini"]
        assert result["failed"] == []
        mock_uninstall.assert_called_once_with("gemini")

    @patch("claif_gem.install.uninstall_tool")
    def test_uninstall_failure(self, mock_uninstall):
        """Test failed uninstallation."""
        mock_uninstall.return_value = False
        
        result = uninstall_gemini()
        
        assert result["uninstalled"] == []
        assert result["failed"] == ["gemini"]
        assert result["message"] == "gemini uninstallation failed"


class TestIsGeminiInstalled:
    """Test suite for is_gemini_installed function."""

    @patch("claif_gem.install.get_install_location")
    def test_installed_as_file(self, mock_get_location):
        """Test when gemini is installed as a file."""
        install_dir = Path("/tmp/claif/bin")
        mock_get_location.return_value = install_dir
        
        with patch("pathlib.Path.exists") as mock_exists:
            with patch("pathlib.Path.is_file") as mock_is_file:
                mock_exists.return_value = True
                mock_is_file.return_value = True
                
                assert is_gemini_installed() is True

    @patch("claif_gem.install.get_install_location")
    def test_installed_as_directory(self, mock_get_location):
        """Test when gemini is installed as a directory."""
        install_dir = Path("/tmp/claif/bin")
        mock_get_location.return_value = install_dir
        
        # First exists() check returns False (not a file), second returns True (is a dir)
        with patch("pathlib.Path.exists", side_effect=[False, True]):
            with patch("pathlib.Path.is_dir", return_value=True):
                assert is_gemini_installed() is True

    @patch("claif_gem.install.get_install_location")
    def test_not_installed(self, mock_get_location):
        """Test when gemini is not installed."""
        install_dir = Path("/tmp/claif/bin")
        mock_get_location.return_value = install_dir
        
        with patch("pathlib.Path.exists", return_value=False):
            assert is_gemini_installed() is False


class TestGetGeminiStatus:
    """Test suite for get_gemini_status function."""

    @patch("claif_gem.install.is_gemini_installed")
    @patch("claif_gem.install.get_install_location")
    def test_status_installed(self, mock_get_location, mock_is_installed):
        """Test status when gemini is installed."""
        mock_is_installed.return_value = True
        mock_get_location.return_value = Path("/home/user/.claif/bin")
        
        status = get_gemini_status()
        
        assert status["installed"] is True
        assert status["path"] == "/home/user/.claif/bin/gemini"
        assert status["type"] == "bundled (claif-owned)"

    @patch("claif_gem.install.is_gemini_installed")
    def test_status_not_installed(self, mock_is_installed):
        """Test status when gemini is not installed."""
        mock_is_installed.return_value = False
        
        status = get_gemini_status()
        
        assert status["installed"] is False
        assert status["path"] is None
        assert status["type"] is None