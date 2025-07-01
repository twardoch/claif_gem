# TODO for CLAIF_GEM

## v1.0 Released ✅

### Completed for v1.0 (2025-01-02)
- ✅ Fix imports to work without local claif package
  - ✅ Make claif import optional with try/except
  - ✅ Provide fallback types if claif not available (created _compat module)
  - ✅ Update pyproject.toml to handle missing claif gracefully
  
- ✅ Update logging to use loguru
  - ✅ Replace all get_logger() calls with direct loguru import
  - ✅ Simple logger.debug(), logger.error(), logger.warning() calls

- ✅ Core functionality
  - ✅ Subprocess-based Gemini CLI integration
  - ✅ Cross-platform CLI discovery
  - ✅ Fire-based CLI with rich output
  - ✅ Async support with anyio
  - ✅ Error handling and timeouts
  - ✅ Comprehensive documentation

## v1.1 - Next Release

### 🔴 High Priority
- [ ] Add comprehensive test coverage
  - [ ] Test CLI discovery logic with mocks
  - [ ] Test command construction variations
  - [ ] Test output parsing (JSON and text edge cases)
  - [ ] Mock subprocess for reliable tests
  - [ ] Integration tests with CLAIF core
  
- [ ] Verify packaging and distribution
  - [ ] Test `hatch build` on multiple platforms
  - [ ] Test pip install from PyPI
  - [ ] Verify CLI entry points on Windows
  
### 🟡 Medium Priority
- [ ] Improve error messages
  - [ ] Better guidance when Gemini CLI not found (suggest npm install)
  - [ ] Clear subprocess failure reasons
  - [ ] Helpful timeout messages with suggestions
  
- [ ] Platform-specific testing
  - [ ] Verify Windows path discovery
  - [ ] Test Linux package manager installs
  - [ ] Document platform-specific setup
  
### 🟢 Low Priority
- [ ] Add GitHub Actions workflow
  - [ ] Basic CI/CD pipeline
  - [ ] Run tests on Python 3.12+
  - [ ] Automated release process
  
- [ ] Performance improvements
  - [ ] Subprocess reuse for multiple queries
  - [ ] Better SIGINT handling
  - [ ] Optimize stderr capture

## v2.0 - Future Major Release

### Performance
- Connection pooling
- Response caching
- Parallel query support
- Subprocess reuse

### Features
- Direct Gemini API support
- Session management
- Tool approval handling
- Advanced retry logic
- Multi-model orchestration
- Configuration file support

### Developer Experience  
- Plugin system
- Custom transports
- Advanced logging
- Metrics collection
- Debug mode

## Quick Wins for v1.1

1. Add pytest fixtures for subprocess mocking (1 hour)
2. Create 5-10 unit tests covering core functionality (2 hours)
3. Test on Windows VM or CI (1 hour)
4. Improve error messages with actionable suggestions (30 min)

## Definition of Done for v1.1

- [ ] 80%+ test coverage on core modules
- [ ] All tests pass on Python 3.12+
- [ ] Verified working on Windows, macOS, Linux
- [ ] Published to PyPI
- [ ] GitHub Actions CI running
- [ ] No regression from v1.0 features