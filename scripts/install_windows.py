#!/usr/bin/env python3
"""Windows-specific installation helper for Gemini CLI."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def check_npm():
    """Check if npm is available."""
    return shutil.which("npm") is not None


def check_bun():
    """Check if bun is available."""
    return shutil.which("bun") is not None


def get_npm_global_path():
    """Get npm global installation path."""
    try:
        result = subprocess.run(
            ["npm", "root", "-g"],
            capture_output=True,
            text=True,
            check=True
        )
        return Path(result.stdout.strip()).parent
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def install_with_npm():
    """Install Gemini CLI using npm."""
    print("Installing Gemini CLI with npm...")
    try:
        subprocess.run(
            ["npm", "install", "-g", "@google/gemini-cli"],
            check=True
        )
        print("✓ Gemini CLI installed successfully with npm")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install with npm: {e}")
        return False


def install_with_bun():
    """Install Gemini CLI using bun."""
    print("Installing Gemini CLI with bun...")
    try:
        subprocess.run(
            ["bun", "add", "-g", "@google/gemini-cli"],
            check=True
        )
        print("✓ Gemini CLI installed successfully with bun")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install with bun: {e}")
        return False


def create_wrapper_scripts():
    """Create Windows wrapper scripts in Claif bin directory."""
    claif_bin = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "claif" / "bin"
    claif_bin.mkdir(parents=True, exist_ok=True)
    
    # Find the installed gemini location
    gemini_cmd = shutil.which("gemini")
    if not gemini_cmd:
        npm_path = get_npm_global_path()
        if npm_path:
            gemini_cmd = npm_path / "gemini.cmd"
            if not gemini_cmd.exists():
                gemini_cmd = npm_path / "@google" / "gemini-cli" / "bin" / "gemini"
    
    if not gemini_cmd or not Path(gemini_cmd).exists():
        print("✗ Could not find installed Gemini CLI")
        return False
    
    # Create batch wrapper
    batch_wrapper = claif_bin / "gemini.cmd"
    batch_content = f'''@echo off
"{gemini_cmd}" %*
'''
    batch_wrapper.write_text(batch_content)
    print(f"✓ Created batch wrapper: {batch_wrapper}")
    
    # Create PowerShell wrapper
    ps_wrapper = claif_bin / "gemini.ps1"
    ps_content = f'''& "{gemini_cmd}" @args
exit $LASTEXITCODE
'''
    ps_wrapper.write_text(ps_content)
    print(f"✓ Created PowerShell wrapper: {ps_wrapper}")
    
    # Add to PATH if not present
    current_path = os.environ.get("PATH", "")
    if str(claif_bin) not in current_path:
        print(f"\n⚠ Add {claif_bin} to your PATH to use 'gemini' command globally")
        print("\nTo add to PATH for current session:")
        print(f'  Command Prompt: set PATH=%PATH%;{claif_bin}')
        print(f'  PowerShell: $env:PATH += ";{claif_bin}"')
    
    return True


def main():
    """Main installation function."""
    if platform.system() != "Windows":
        print("This script is for Windows only.")
        sys.exit(1)
    
    print("=== Gemini CLI Windows Installation ===\n")
    
    # Check for package managers
    has_npm = check_npm()
    has_bun = check_bun()
    
    if not has_npm and not has_bun:
        print("✗ Neither npm nor bun found.")
        print("\nPlease install Node.js (includes npm) from:")
        print("  https://nodejs.org/")
        print("\nOr install bun from:")
        print("  https://bun.sh/")
        sys.exit(1)
    
    # Try installation
    installed = False
    
    if has_bun:
        # Prefer bun for speed
        installed = install_with_bun()
    
    if not installed and has_npm:
        installed = install_with_npm()
    
    if not installed:
        print("\n✗ Failed to install Gemini CLI")
        sys.exit(1)
    
    # Create wrapper scripts
    print("\nCreating Windows wrapper scripts...")
    if create_wrapper_scripts():
        print("\n✓ Installation complete!")
    else:
        print("\n⚠ Installation completed but wrapper creation failed")
    
    # Test installation
    print("\nTesting installation...")
    try:
        result = subprocess.run(
            ["gemini", "--version"],
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0:
            print(f"✓ Gemini CLI is working: {result.stdout.strip()}")
        else:
            print("⚠ Gemini CLI installed but not responding to --version")
    except Exception as e:
        print(f"⚠ Could not test Gemini CLI: {e}")


if __name__ == "__main__":
    main()