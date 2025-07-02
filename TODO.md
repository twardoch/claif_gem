# claif_gem TODO List - v1.x Stable MVP

## Immediate Priority (v1.0.7)

### Unit Testing
- [ ] Add pytest test suite for all modules
- [ ] Test transport.py subprocess handling
- [ ] Test client.py message conversion
- [ ] Test CLI discovery logic
- [ ] Test command construction
- [ ] Test install.py functionality
- [ ] Mock subprocess operations
- [ ] Test timeout and cancellation
- [ ] Achieve 80%+ code coverage

### Subprocess Cleanup
- [ ] Handle process termination cleanly
- [ ] Fix resource leaks
- [ ] Proper async cleanup

### Error Messages
- [ ] Add context to subprocess errors
- [ ] Clear API key error messages
- [ ] Better error display

## Short-term Priority (v1.1.0)

### Integration Testing
- [ ] Test with real Gemini CLI
- [ ] Test auto-install flow
- [ ] Test different response formats
- [ ] Test error conditions
- [ ] Cross-platform compatibility

### Cross-Platform Testing
- [ ] Test all discovery paths
- [ ] Handle Windows .cmd files
- [ ] Support custom install paths
- [ ] Verify executable permissions
- [ ] Handle path spaces correctly
- [ ] Windows path handling
- [ ] macOS security permissions
- [ ] Linux distribution variations
- [ ] WSL compatibility
- [ ] Docker container support

### Documentation
- [ ] Installation guide
- [ ] API key setup guide
- [ ] Model selection guide
- [ ] Auto-approve usage
- [ ] Troubleshooting section

## Medium-term Priority (v1.2.0)

### Advanced Gemini Features
- [ ] Full options support
- [ ] Response metadata
- [ ] Extended CLI options

### Response Caching
- [ ] Implement caching layer
- [ ] Cache invalidation
- [ ] TTL management

### Direct API Option
- [ ] Native Gemini API integration
- [ ] Fallback mechanism
- [ ] Performance comparison

## Testing & Reliability

### Subprocess Reliability
- [ ] Test with slow/hanging processes
- [ ] Verify memory cleanup
- [ ] Test concurrent operations
- [ ] Handle zombie processes

### Gemini-Specific Errors
- [ ] Parse Gemini error formats
- [ ] Handle rate limits gracefully
- [ ] Context length errors
- [ ] Authentication failures
- [ ] Model not found errors

### Installation Robustness
- [ ] Verify npm/bun availability
- [ ] Handle partial installs
- [ ] Support proxy environments
- [ ] Offline install options
- [ ] Version compatibility checks

## Transport Layer Improvements

### Async Operations
- [ ] Proper cleanup on cancellation
- [ ] Handle process groups
- [ ] Stream buffering optimization
- [ ] Backpressure handling
- [ ] Resource leak prevention

### Performance
- [ ] Profile subprocess overhead
- [ ] Optimize JSON/text parsing
- [ ] Reduce memory usage
- [ ] Connection reuse
- [ ] Response streaming

## Gemini-Specific Features

### Options Support
- [ ] Validate all Gemini options
- [ ] Handle max-context-length
- [ ] Support auto-approve mode
- [ ] Implement yes-mode properly
- [ ] System prompt handling

### Response Handling
- [ ] Parse structured responses
- [ ] Handle streaming correctly
- [ ] Support different output formats
- [ ] Error response parsing
- [ ] Metadata extraction

## Code Organization

### Key Module Improvements

#### transport.py
- [ ] Better process lifecycle management
- [ ] Improved CLI discovery logic
- [ ] Enhanced error context
- [ ] Performance monitoring

#### client.py
- [ ] Message validation
- [ ] Error wrapping
- [ ] Connection pooling
- [x] Retry logic ✅ COMPLETED - Implemented tenacity-based retry with exponential backoff

#### cli.py
- [ ] Standardized help text
- [ ] Progress indicators
- [ ] Better error display
- [ ] Command shortcuts

## Quality Standards

### Testing Focus
- [ ] Mock all anyio.open_process calls
- [ ] Test CLI discovery paths
- [ ] Verify command construction
- [ ] Test JSON/text parsing
- [ ] Validate error handling

### Performance Testing
- [ ] Subprocess spawn overhead
- [ ] Response parsing speed
- [ ] Memory usage profiling
- [ ] Concurrent operations
- [ ] Large response handling

## Success Metrics

- [ ] **Reliability**: 99.9% success rate for subprocess operations
- [ ] **Performance**: < 100ms overhead per operation
- [ ] **Testing**: 80%+ test coverage with mocks
- [ ] **Error Handling**: Clear, actionable error messages
- [ ] **Cross-Platform**: Verified on Windows, macOS, Linux
- [ ] **Documentation**: Complete user and API docs
- [ ] **Installation**: Auto-install works everywhere

## Non-Goals for v1.x

- Complex UI features
- Custom protocol extensions
- Database persistence
- Multi-user support
- Response transformation