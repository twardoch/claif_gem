# claif_gem Development Plan - v1.x Stable MVP

## Overview

`claif_gem` is the Gemini provider for Claif, wrapping Google's Gemini CLI tool. The goal for v1.x is to create a stable, reliable MVP with comprehensive testing, cross-platform compatibility, and excellent subprocess management.

## Current Status (v1.0.7-dev)

**Core Functionality**: Working Gemini CLI integration ✅
**Auto-Install**: Automatic CLI installation when missing ✅
**Subprocess Management**: Async with anyio ✅
**CLI Interface**: Fire-based with clean output ✅
**Retry Logic**: Tenacity-based retry with exponential backoff ✅
**Error Detection**: Smart detection of quota/rate limit errors ✅
**Testing**: Comprehensive retry logic test suite ✅

## MVP v1.x Improvement Plan

### 1. Testing & Reliability (Critical)

#### Unit Testing
- [ ] Add pytest test suite for all modules
  - [ ] Test transport.py subprocess handling
  - [ ] Test client.py message conversion
  - [ ] Test CLI discovery logic
  - [ ] Test command construction
  - [ ] Test install.py functionality
- [ ] Mock subprocess operations
- [ ] Test timeout and cancellation
- [ ] Achieve 80%+ code coverage

#### Integration Testing  
- [ ] Test with real Gemini CLI
- [ ] Test auto-install flow
- [ ] Test different response formats
- [ ] Test error conditions
- [ ] Cross-platform compatibility

#### Subprocess Reliability
- [ ] Handle process termination cleanly
- [ ] Test with slow/hanging processes
- [ ] Verify memory cleanup
- [ ] Test concurrent operations
- [ ] Handle zombie processes

### 2. Error Handling & Messages

#### Better Error Context
- [ ] Add context to subprocess errors
- [ ] Clear API key error messages
- [ ] Installation failure guidance
- [ ] Network timeout explanations
- [ ] Model availability errors

#### Gemini-Specific Errors
- [ ] Parse Gemini error formats
- [ ] Handle rate limits gracefully
- [ ] Context length errors
- [ ] Authentication failures
- [ ] Model not found errors

### 3. CLI Discovery & Platform Support

#### Cross-Platform Discovery
- [ ] Test all discovery paths
- [ ] Handle Windows .cmd files
- [ ] Support custom install paths
- [ ] Verify executable permissions
- [ ] Handle path spaces correctly

#### Platform-Specific Testing
- [ ] Windows path handling
- [ ] macOS security permissions
- [ ] Linux distribution variations
- [ ] WSL compatibility
- [ ] Docker container support

### 4. Transport Layer Improvements

#### Async Operations
- [ ] Proper cleanup on cancellation
- [ ] Handle process groups
- [ ] Stream buffering optimization
- [ ] Backpressure handling
- [ ] Resource leak prevention

#### Performance
- [ ] Profile subprocess overhead
- [ ] Optimize JSON/text parsing
- [ ] Reduce memory usage
- [ ] Connection reuse
- [ ] Response streaming

### 5. Gemini-Specific Features

#### Options Support
- [ ] Validate all Gemini options
- [ ] Handle max-context-length
- [ ] Support auto-approve mode
- [ ] Implement yes-mode properly
- [ ] System prompt handling

#### Response Handling
- [ ] Parse structured responses
- [ ] Handle streaming correctly
- [ ] Support different output formats
- [ ] Error response parsing
- [ ] Metadata extraction

### 6. Documentation & Examples

#### User Documentation
- [ ] Installation guide
- [ ] API key setup guide
- [ ] Model selection guide
- [ ] Auto-approve usage
- [ ] Troubleshooting section

#### Developer Documentation
- [ ] Architecture overview
- [ ] Transport design patterns
- [ ] Testing approach
- [ ] Contributing guide
- [ ] Performance tips

## Architecture Improvements

### Module Structure
```
claif_gem/
├── __init__.py        # Clean public API
├── transport.py       # Robust subprocess layer
├── client.py         # Tested client wrapper
├── cli.py            # User-friendly CLI
├── types.py          # Well-defined types
├── install.py        # Cross-platform installer
└── utils.py          # Shared utilities
```

### Key Improvements Needed

#### transport.py
- Better process lifecycle management
- Improved CLI discovery logic
- Enhanced error context
- Performance monitoring

#### client.py
- Message validation
- Error wrapping
- Connection pooling
- Retry logic

#### cli.py
- Standardized help text
- Progress indicators
- Better error display
- Command shortcuts

## Quality Standards

### Code Quality
- 100% type hint coverage
- Comprehensive docstrings
- Maximum cyclomatic complexity: 10
- Clear error messages
- Consistent naming

### Testing Standards
- Unit tests for all functions
- Integration tests for workflows
- Mock all subprocess calls
- Test all error paths
- Cross-platform verification

### Documentation Standards
- Complete README
- API documentation
- Architecture diagrams
- Troubleshooting guide
- Platform-specific notes

## Success Criteria for v1.x

1.  **Reliability**: 99.9% success rate for subprocess operations
2.  **Performance**: < 100ms overhead per operation
3.  **Testing**: 80%+ test coverage with mocks
4.  **Error Handling**: Clear, actionable error messages
5.  **Cross-Platform**: Verified on Windows, macOS, Linux
6.  **Documentation**: Complete user and API docs
7.  **Installation**: Auto-install works everywhere

## Development Priorities

### Immediate (v1.0.7)
1.  Add pytest test suite for all modules
2.  Test transport.py subprocess handling
3.  Test client.py message conversion
4.  Test CLI discovery logic
5.  Test command construction
6.  Test install.py functionality
7.  Mock subprocess operations
8.  Test timeout and cancellation
9.  Achieve 80%+ code coverage
10. Handle process termination cleanly
11. Fix resource leaks
12. Proper async cleanup
13. Add context to subprocess errors
14. Clear API key error messages
15. Better error display

### Short-term (v1.1.0)
1.  Cross-platform testing
2.  Complete documentation
3.  Performance optimization

### Medium-term (v1.2.0)
1.  Advanced Gemini features
2.  Response caching
3.  Direct API option

## Non-Goals for v1.x

-   Complex UI features
-   Custom protocol extensions
-   Database persistence
-   Multi-user support
-   Response transformation

## Testing Strategy

### Unit Test Focus
-   Mock all anyio.open_process calls
-   Test CLI discovery paths
-   Verify command construction
-   Test JSON/text parsing
-   Validate error handling

### Integration Test Focus
-   Real CLI execution
-   Cross-platform paths
-   Installation verification
-   Network failure scenarios
-   Model selection

### Performance Testing
-   Subprocess spawn overhead
-   Response parsing speed
-   Memory usage profiling
-   Concurrent operations
-   Large response handling

Keep the codebase lean and focused on being a reliable Gemini provider for Claif.
