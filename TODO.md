# claif_gem TODO List

## Essential MVP Tasks

### Core Functionality
- [ ] Add proper error handling for missing API keys  
- [ ] Implement async cleanup in transport layer
- [ ] Add timeout handling for long-running queries
- [ ] Improve gemini-cli subprocess communication

### Auto-Install Support (Issue #201) - ✅ COMPLETED
- [x] Implement auto-install of gemini-cli when missing
- [x] Add CLI detection and installation prompts  
- [x] Integrate with bun bundling for offline installation
- [x] Wire existing install commands as exception handlers

### Rich Dependencies - ✅ COMPLETED
- [x] Remove all rich dependencies from CLI
- [x] Replace rich.console with loguru logging
- [x] Simplify progress indicators and output formatting
- [x] Use plain text output with clear formatting

### Testing
- [ ] Create integration tests with mocked Gemini responses
- [ ] Add unit tests for transport layer
- [ ] Test CLI entry point installation
- [ ] Add --version flag for CLI

### Documentation
- [ ] Add troubleshooting guide
- [ ] Document all CLI commands with examples
- [ ] Create getting started guide

## Known Issues
- [ ] No validation for gemini-cli responses
- [ ] Subprocess error handling could be more robust
- [ ] Image support not yet implemented

## Technical Debt
- [ ] Improve error messages with actionable suggestions
- [ ] Add more specific exception types
- [ ] Consider using pathlib throughout instead of string paths

## Contributing Guidelines

- [ ] Create CONTRIBUTING.md
- [ ] Set up issue templates
- [ ] Create PR template
- [ ] Define code review process

## Notes

- Focus on stability and reliability for v1.x releases
- Keep the wrapper thin and maintainable
- Prioritize developer experience
- Test thoroughly with real gemini-cli before each release

### Core Testing
- [ ] Add comprehensive test coverage (currently minimal)
- [ ] Test CLI discovery logic with mocks
- [ ] Test command construction variations
- [ ] Test output parsing (JSON and text edge cases)
- [ ] Mock subprocess for reliable tests
- [ ] Integration tests withClaif core

### Cross-Platform Reliability
- [ ] Verify packaging and distribution
- [ ] Test `hatch build` on multiple platforms
- [ ] Test pip install from PyPI
- [ ] Verify CLI entry points on Windows
- [ ] Test Linux package manager installs

### Error Handling
- [ ] Improve error messages for missing CLI
- [ ] Better guidance when Gemini CLI not found
- [ ] Clear subprocess failure reasons
- [ ] Helpful timeout messages with suggestions

## Technical Improvements

### Code Quality
- [ ] Platform-specific testing
- [ ] Better SIGINT handling
- [ ] Optimize stderr capture
- [ ] Add GitHub Actions workflow

### Performance
- [ ] Subprocess reuse for multiple queries (future)
- [ ] Connection pooling (future)
- [ ] Response caching (future)

## Definition of Done

- [ ] 80%+ test coverage on core modules
- [ ] All tests pass on Python 3.12+
- [ ] Verified working on Windows, macOS, Linux
- [x] No rich dependencies
- [ ] Auto-install functionality working
- [ ] Published to PyPI