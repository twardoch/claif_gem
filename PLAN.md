# claif_gem Development Plan - Production MVP

## Project Vision

`claif_gem` is a production-ready wrapper around Google's Gemini CLI that integrates seamlessly with theClaif ecosystem. The focus is on delivering a stable, cross-platform tool that auto-installs dependencies and works reliably out of the box.

## MVP Requirements (v1.1)

### Core Functionality
1. **Gemini CLI Integration**
   - Robust subprocess wrapper for gemini-cli
   - Cross-platform CLI discovery and execution
   - Async message streaming with proper error handling
   - Loguru-based logging (no rich dependencies)

2. **Auto-Install Support (Issue #201)**
   - Detect missing gemini-cli installation
   - Auto-install via npm when missing
   - Integrate with bun bundling for offline scenarios
   - Clear user guidance during installation process

3. **Streamlined CLI Interface**
   - Fire-based CLI with simple, clean output
   - Essential commands: ask, stream, health, models
   - Version information and comprehensive help
   - Proper error handling with actionable messages

4. **Cross-Platform Reliability**
   - Works seamlessly on Windows, macOS, Linux
   - Handles different Node.js installation paths
   - Robust subprocess management with timeouts
   - Platform-specific path discovery

### Simplified Architecture

```
claif_gem/
├── transport.py   # Subprocess management & CLI discovery
├── client.py      #Claif provider interface
├── cli.py         # Fire-based CLI (loguru only)
├── types.py       # Type definitions
├── install.py     # Auto-install functionality
└── _compat/       # Compatibility layer
```

## Implementation Plan

### Phase 1: Dependency Cleanup
- [ ] Remove all rich imports and dependencies
- [ ] Replace rich.console with loguru logging
- [ ] Simplify progress indicators and live updates
- [ ] Use clean text-based output formatting

### Phase 2: Auto-Install Integration
- [ ] Implement gemini-cli detection logic
- [ ] Add npm installation wrapper
- [ ] Integrate with bun bundling system
- [ ] Provide clear installation prompts and guidance

### Phase 3: Testing & Reliability
- [ ] Comprehensive unit test coverage (80%+)
- [ ] Mock subprocess calls for reliable testing
- [ ] Cross-platform integration tests
- [ ] Error handling and edge case coverage

### Phase 4: Polish & Release
- [ ] Documentation updates with auto-install info
- [ ] Performance testing and optimization
- [ ] Final packaging verification
- [ ] PyPI release with GitHub Actions

## Technical Decisions

### Simplified Dependencies
- **Remove**: rich, complex UI libraries
- **Keep**: loguru, fire, anyio, gemini-cli integration
- **Add**: Auto-install utilities and better error handling

### Error Handling Strategy
- Detect missing CLI gracefully with clear messages
- Provide actionable installation instructions
- Handle subprocess failures with helpful context
- Timeout management with user-friendly messages

### Cross-Platform Support
- Robust CLI discovery across different OS environments
- Handle various Node.js installation paths
- Platform-specific subprocess management
- Consistent behavior across operating systems

## Success Metrics

1. **Usability**: Works with `uvx claif_gem` immediately
2. **Reliability**: Handles missing dependencies gracefully
3. **Performance**: < 100ms overhead per query
4. **Cross-platform**: Tested on Windows, macOS, Linux
5. **Maintainability**: Clean, well-tested codebase

## Quality Gates

### Before Release
- [ ] 80%+ unit test coverage
- [ ] All tests pass on Python 3.12+
- [ ] Cross-platform testing completed
- [ ] No rich dependencies remaining
- [ ] Auto-install functionality verified
- [ ] Documentation complete and accurate

### Post-Release Monitoring
- User feedback on installation experience
- Performance metrics in real-world usage
- Cross-platform compatibility reports
- Integration success withClaif ecosystem

## Future Enhancements (Post-MVP)

### v1.2+ Considerations
- Response caching for improved performance
- Session management capabilities
- Advanced retry logic with exponential backoff
- Connection pooling for multiple queries
- Direct Gemini API integration option

### Non-Goals for MVP
- Complex UI/formatting features
- Advanced configuration management
- Performance optimizations beyond basics
- Extensive plugin systems
- Web interfaces

## Release Strategy

- **v1.1**: Production MVP with auto-install and no rich deps
- **v1.2**: Performance improvements and enhanced features
- **v2.0**: Major enhancements based on user feedback

This plan prioritizes delivering a reliable, user-friendly tool that works immediately upon installation while maintaining the flexibility to grow based on actual usage patterns and feedback.