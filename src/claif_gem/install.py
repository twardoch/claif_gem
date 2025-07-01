# this_file: claif_gem/src/claif_gem/install.py

from loguru import logger

# Import common install functionality
try:
    from claif.install import (
        ensure_bun_installed,
        get_install_location,
        install_npm_package_globally,
        bundle_all_tools,
        install_portable_tool,
        uninstall_tool,
    )
except ImportError:
    logger.error("claif package not found. Please install claif package first.")
    exit(1)


def install_gemini() -> dict:
    """Install Gemini CLI with bundled approach."""
    if not ensure_bun_installed():
        return {"installed": [], "failed": ["gemini"], "message": "bun installation failed"}

    install_dir = get_install_location()

    # Install npm package globally first
    logger.info("Installing @google/gemini-cli...")
    if not install_npm_package_globally("@google/gemini-cli"):
        return {"installed": [], "failed": ["gemini"], "message": "@google/gemini-cli installation failed"}

    # Bundle all tools (this creates the dist directory with all tools)
    logger.info("Bundling CLI tools...")
    dist_dir = bundle_all_tools()
    if not dist_dir:
        return {"installed": [], "failed": ["gemini"], "message": "bundling failed"}

    # Install Gemini specifically
    logger.info("Installing gemini...")
    if install_portable_tool("gemini", install_dir, dist_dir):
        logger.success("🎉 Gemini installed successfully!")
        logger.info("You can now use 'gemini' command from anywhere")
        return {"installed": ["gemini"], "failed": []}
    else:
        return {"installed": [], "failed": ["gemini"], "message": "gemini installation failed"}


def uninstall_gemini() -> dict:
    """Uninstall Gemini CLI."""
    logger.info("Uninstalling gemini...")

    if uninstall_tool("gemini"):
        logger.success("✓ Gemini uninstalled successfully")
        return {"uninstalled": ["gemini"], "failed": []}
    else:
        return {"uninstalled": [], "failed": ["gemini"], "message": "gemini uninstallation failed"}


def is_gemini_installed() -> bool:
    """Check if Gemini is installed."""
    install_dir = get_install_location()
    gemini_executable = install_dir / "gemini"

    return gemini_executable.exists() and gemini_executable.is_file()


def get_gemini_status() -> dict:
    """Get Gemini installation status."""
    if is_gemini_installed():
        install_dir = get_install_location()
        gemini_path = install_dir / "gemini"
        return {"installed": True, "path": str(gemini_path), "type": "bundled (claif-owned)"}
    else:
        return {"installed": False, "path": None, "type": None}
