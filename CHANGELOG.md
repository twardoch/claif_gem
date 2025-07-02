# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.4] - 2025-07-01

### Changed
- Switched from anyio to asyncio for subprocess handling for improved reliability
- Simplified transport layer by using native asyncio subprocess management
- Changed process type annotation from `anyio.Process` to `Any` for flexibility
- Improved command string formatting for debug logging
- Removed empty pass statement in connect method

### Added
- Added reference documentation file (gemini-cli-usage.txt)

### Fixed
- Fixed potential subprocess handling issues by using native asyncio instead of anyio
- Improved error handling during process cleanup operations
- Changed disconnect error logging from WARNING to DEBUG level for cleaner output during cleanup

### Removed
- Removed unused TextReceiveStream import from anyio
- Removed empty lines in _compat/__init__.py

## [1.0.3] - 2025-07-01

[Previous version - no changelog entry]

## [1.0.2] - 2025-07-01

[Previous version - no changelog entry]

## [1.0.1] - 2025-07-01

### Fixed
- Reduced log noise by changing disconnect errors from WARNING to DEBUG level
- Disconnect errors during cleanup are now logged as debug messages since they're expected during normal operation
- Improved error message clarity with context about cleanup operations

### Changed
- Better handling of process termination errors with more appropriate logging levels
- Cleaner command output with reduced warning noise

## [Unreleased]

### Changed
- Updated README.md with comprehensive documentation
- Enhanced pyproject.toml with complete metadata and dependencies
- Improved code organization and type hints
- Added compatibility layer for standalone usage withoutClaif core

## [1.0.0] - 2025-01-02

### Added
- Initial release of`claif_gem` - Google Gemini provider forClaif
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
  - `__init__.py`: Main entry point andClaif interface
  - `cli.py`: Fire-based command-line interface
  - `client.py`: Client orchestration layer
  - `transport.py`: Subprocess management and CLI communication
  - `types.py`: Type definitions and data classes
- Comprehensive documentation:
  - CLAUDE.md: Development guidelines forClaif ecosystem
  - GEMINI.md: Gemini-specific development notes
  - AGENTS.md: Virtual team collaboration guide
- Reference materials for Gemini CLI integration

### Dependencies
- `claif>=1.0.1`: CoreClaif framework
- `anyio>=4.0.0`: Async I/O library for subprocess management
- `fire>=0.5.0`: CLI framework
- `rich>=13.0.0`: Terminal formatting and progress display
- `loguru>=0.7.0`: Logging framework
- Additional utilities: click, shell-functools, icecream