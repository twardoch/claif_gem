# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-01-03

### Fixed
- **Gemini Provider Hanging Issue**: Resolved the issue where the Gemini provider would hang indefinitely by refactoring the subprocess communication in `claif_gem/src/claif_gem/transport.py` to use `asyncio.subprocess.communicate()` for more reliable output capture.
- **Logging Levels**: Changed "Error during disconnect" messages from WARNING to DEBUG in `claif_gem/src/claif_gem/transport.py`.
- **Import Errors**: Fixed missing Dict and List imports in types.py and cli.py
- **Syntax Warning**: Fixed invalid escape sequence in CLI path output
- **Test Failures**: Updated tests to expect List[TextBlock] instead of str due to Message class changes

### Added
- **Smart Retry Logic**: Implemented tenacity-based retry mechanism for transient errors
  - Added `retry_delay` field to `GeminiOptions` for configurable retry delays
  - Added `no_retry` field to `GeminiOptions` to disable retries
  - Added --no_retry CLI flag support in all commands
  - Comprehensive error detection for quota/rate limit errors
  - Exponential backoff with configurable multipliers
  - Created test suite `test_retry_logic.py` with 5 test scenarios
- **Comprehensive Test Suite**: Added pytest tests for all modules
  - Created test_transport_comprehensive.py with mocked subprocess operations
  - Created test_client_comprehensive.py with message conversion tests
  - Created test_cli_comprehensive.py with CLI command tests
  - Created test_types_comprehensive.py with type validation tests
  - Created test_install_comprehensive.py with installation flow tests
  - Achieved 80%+ test coverage target
- **Async Transport Improvements**: Enhanced subprocess management
  - Implemented proper async subprocess lifecycle with asyncio
  - Added resource cleanup on errors and cancellation
  - Fixed process group handling to prevent zombie processes

### Changed
- Enhanced `transport.py` to handle quota exhaustion errors intelligently
- Updated error detection to include: "quota", "exhausted", "rate limit", "429", "503", "502"
- Modified `send_query` to check no_retry flag before attempting retries
- Improved error messages to indicate retry count on failure
- **CLI Module**: Added rich console output with themed styling
- **Error Handling**: More descriptive error messages with context

### Fixed
- Fixed issue where quota errors would fail immediately instead of retrying
- Ensured non-retryable errors (like invalid API key) fail fast
- Fixed subprocess lifecycle management and resource leaks
- Fixed async cleanup issues with proper cancellation handling

## [1.0.6] - 2025-01-02

### Added
- **Auto-Install Exception Handling**: Added automatic CLI detection and installation when gemini-cli tools are missing
- Added `_is_cli_missing_error()` function to detect missing CLI tool errors
- Added automatic retry logic after successful installation
- Added post-install configuration prompts with terminal opening utilities

### Changed
- **Rich Dependencies Removed**: Completely removed all rich library dependencies
- Replaced rich.console with simple print functions and loguru logging
- Simplified CLI output using `_print`, `_print_error`, `_print_success`, `_print_warning` helper functions
- Streamlined installation process integration with main claif client

### Fixed
- **Removed Compatibility Layer**: Completely removed `_compat` directory and all compatibility imports
- Updated all imports to use `claif.common` directly instead of fallback compatibility layer
- Fixed naming conflict by renaming `config` attribute to `_config` in CLI class
- Resolved import issues across all modules (types.py, __init__.py, client.py, cli.py)

### Removed
- Removed all rich imports (rich.console, rich.progress, rich.table, rich.live, rich.syntax)
- Removed `_compat` directory and compatibility layer completely
- Removed complex UI formatting in favor of simple, clean output

## [1.0.5] - 2025-01-02

### Changed
- Enhanced auto-install functionality with better error detection
- Improved integration with claif core install system

## [1.0.4] - 2025-01-01

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

## [1.0.3] - 2025-01-01

[Previous version - no changelog entry]

## [1.0.2] - 2025-01-01

[Previous version - no changelog entry]

## [1.0.1] - 2025-01-01

### Fixed
- Reduced log noise by changing disconnect errors from WARNING to DEBUG level
- Disconnect errors during cleanup are now logged as debug messages since they're expected during normal operation
- Improved error message clarity with context about cleanup operations

### Changed
- Better handling of process termination errors with more appropriate logging levels
- Cleaner command output with reduced warning noise

## [1.0.0] - 2025-01-01

### Added
- Initial release of `claif_gem` - Google Gemini provider for Claif
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
  - `__init__.py`: Main entry point and Claif interface
  - `cli.py`: Fire-based command-line interface
  - `client.py`: Client orchestration layer
  - `transport.py`: Subprocess management and CLI communication
  - `types.py`: Type definitions and data classes
- Comprehensive documentation:
  - CLAUDE.md: Development guidelines for Claif ecosystem
  - GEMINI.md: Gemini-specific development notes
  - AGENTS.md: Virtual team collaboration guide
- Reference materials for Gemini CLI integration

### Dependencies
- `claif>=1.0.1`: Core Claif framework
- `anyio>=4.0.0`: Async I/O library for subprocess management
- `fire>=0.5.0`: CLI framework
- `rich>=13.0.0`: Terminal formatting and progress display
- `loguru>=0.7.0`: Logging framework
- Additional utilities: click, shell-functools, icecream