# this_file: claif_gem/src/claif_gem/install.py

import shutil
from pathlib import Path

from loguru import logger

# Import common install functionality
try:
    from claif.common.utils import prompt_tool_configuration
    from claif.install import (
        bundle_all_tools,
        ensure_bun_installed,
        get_install_location,
        install_npm_package_globally,
        uninstall_tool,
    )
except ImportError:
    # Fallback if claif package not available
    logger.warning("claif package not found, using local implementations")
    from claif_gem.install_fallback import (
        bundle_all_tools,
        ensure_bun_installed,
        get_install_location,
        install_npm_package_globally,
        uninstall_tool,
    )

    def prompt_tool_configuration(tool_name: str, config_commands: list[str]) -> None:
        """Fallback implementation for tool configuration prompt."""
        if config_commands:
            for _cmd in config_commands:
                pass


def install_gemini_bundled(install_dir: Path, dist_dir: Path) -> bool:
    """Install bundled Gemini (portable tool)."""
    try:
        gemini_source = dist_dir / "gemini" / "gemini"
        if not gemini_source.exists():
            logger.error(f"Bundled Gemini not found at {gemini_source}")
            return False

        # Copy the executable directly
        gemini_target = install_dir / "gemini"
        shutil.copy2(gemini_source, gemini_target)
        gemini_target.chmod(0o755)

        logger.success(f"✓ Gemini installed at {gemini_target}")
        return True

    except Exception as e:
        logger.error(f"Failed to install Gemini: {e}")
        return False


def install_gemini() -> dict:
    """Install Gemini CLI with bundled approach."""
    if not ensure_bun_installed():
        return {"installed": [], "failed": ["gemini"], "message": "bun installation failed"}

    install_dir = get_install_location()

    # Install npm package globally first
    logger.info("Installing @google-ai/gemini-cli...")
    if not install_npm_package_globally("@google-ai/gemini-cli"):
        return {"installed": [], "failed": ["gemini"], "message": "@google-ai/gemini-cli installation failed"}

    # Bundle all tools (this creates the dist directory with all tools)
    logger.info("Bundling CLI tools...")
    dist_dir = bundle_all_tools()
    if not dist_dir:
        return {"installed": [], "failed": ["gemini"], "message": "bundling failed"}

    # Install Gemini specifically
    logger.info("Installing gemini...")
    if install_gemini_bundled(install_dir, dist_dir):
        logger.success("🎉 Gemini installed successfully!")
        logger.info("You can now use 'gemini' command from anywhere")

        # Prompt for configuration
        config_commands = [
            "gemini auth login",
            "gemini config set --api-key YOUR_API_KEY",
            "gemini --help",
        ]
        prompt_tool_configuration("Gemini", config_commands)

        return {"installed": ["gemini"], "failed": []}
    return {"installed": [], "failed": ["gemini"], "message": "gemini installation failed"}


def uninstall_gemini() -> dict:
    """Uninstall Gemini CLI."""
    logger.info("Uninstalling gemini...")

    if uninstall_tool("gemini"):
        logger.success("✓ Gemini uninstalled successfully")
        return {"uninstalled": ["gemini"], "failed": []}
    return {"uninstalled": [], "failed": ["gemini"], "message": "gemini uninstallation failed"}


def is_gemini_installed() -> bool:
    """Check if Gemini is installed."""
    install_dir = get_install_location()
    gemini_executable = install_dir / "gemini"
    gemini_dir = install_dir / "gemini"

    return (gemini_executable.exists() and gemini_executable.is_file()) or (gemini_dir.exists() and gemini_dir.is_dir())


def get_gemini_status() -> dict:
    """Get Gemini installation status."""
    if is_gemini_installed():
        install_dir = get_install_location()
        gemini_path = install_dir / "gemini"
        return {"installed": True, "path": str(gemini_path), "type": "bundled (claif-owned)"}
    return {"installed": False, "path": None, "type": None}
