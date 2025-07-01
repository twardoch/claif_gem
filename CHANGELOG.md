# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Updated README.md with comprehensive documentation
- Enhanced pyproject.toml with complete metadata and dependencies
- Improved code organization and type hints
- Added compatibility layer for standalone usage without CLAIF core

## [1.0.0] - 2025-01-02

### Added
- Initial release of CLAIF_GEM - Google Gemini provider for CLAIF
- Fire-based CLI with commands: `query`, `stream`, `health`, `models`, `config`
- Async/await support for all operations
- Subprocess-based integration with Gemini CLI binary
- Automatic CLI discovery across Windows, macOS, and Linux
- Support for auto-approval and yes-mode options
- Rich terminal output with progress indicators
- Comprehensive error handling with timeout protection
- Type hints for better IDE support
- Environment variable configuration support
- Module structure with clear separation of concerns:
  - `__init__.py`: Main entry point and CLAIF interface
  - `cli.py`: Fire-based command-line interface
  - `client.py`: Client orchestration layer
  - `transport.py`: Subprocess management and CLI communication
  - `types.py`: Type definitions and data classes
- Comprehensive documentation:
  - CLAUDE.md: Development guidelines for CLAIF ecosystem
  - GEMINI.md: Gemini-specific development notes
  - AGENTS.md: Virtual team collaboration guide
- Reference materials for Gemini CLI integration

### Dependencies
- `claif>=1.0.1`: Core CLAIF framework
- `anyio>=4.0.0`: Async I/O library for subprocess management
- `fire>=0.5.0`: CLI framework
- `rich>=13.0.0`: Terminal formatting and progress display
- `loguru>=0.7.0`: Logging framework
- Additional utilities: click, shell-functools, icecream