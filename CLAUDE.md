
#Claif (Command-Line Artificial Intelligence Framework)

Claif (Command-Line AI Framework) is a unified interface for interacting with various large language models (LLMs) from the command line.

The project consists of four Github repositories and Python packages:

- [`claif_cla`](https://github.com/twardoch/claif_cla/): CLI and Python package that wraps the [`claude_code_sdk`](https://github.com/anthropics/claude-code-sdk-python) package for interacting with Anthropic’s [Claude Code CLI](https://github.com/anthropics/claude-code) agentic CLI toolkit based on their Claude models.
- [`claif_cod`](https://github.com/twardoch/claif_cod/): CLI and Python package for interacting with OpenAI’s new [Codex CLI](https://github.com/openai/codex) agentic CLI toolkit based on OpenAI’s models.
- [`claif_gem`](https://github.com/twardoch/claif_gem/): CLI and Python package for that wraps the [Gemini CLI](https://github.com/google-gemini/gemini-cli/) agentic CLI toolkit based on Google’s Gemini models.
- [`claif`](https://github.com/twardoch/claif/): The top-levelClaif framework that provides the main building blocks, including the client, server, and provider integrations.

This document provides comprehensive development guidelines for all packages in the Claif ecosystem.

## 1. This very project overview

### 1.1. `claif_gem`:Claif provider for the Google Gemini CLI toolkit

[`claif_gem`](https://github.com/twardoch/claif_gem/): CLI and Python package for that wraps the [Gemini CLI](https://github.com/google-gemini/gemini-cli/) agentic CLI toolkit based on Google’s Gemini models.

**Key Responsibilities:**

- Gemini CLI subprocess management
- Auto-approval and yes-mode handling
- Context length management
- System prompt configuration

**Development Focus:**

- Robust subprocess handling
- CLI argument parsing
- Timeout and error recovery
- Cross-platform compatibility

## 2. Other projects in the Claif ecosystem

### 2.1. `claif`:Claif core framework

[`claif`](https://github.com/twardoch/claif/) is the top-levelClaif framework that provides the main building blocks, including the client, server, and provider integrations.

**Key Responsibilities:**

- Provider abstraction and routing
- Plugin discovery and loading
- Common types and error handling
- Configuration management
- CLI framework (Fire-based)
- MCP server implementation

**Development Focus:**

- Maintain strict API compatibility
- Ensure provider independence
- Keep dependencies minimal
- Prioritize extensibility

### 2.2. `claif_cla`:Claif provider for the Anthropic Claude Code CLI toolkit

[`claif_cla`](https://github.com/twardoch/claif_cla/) is a CLI and Python package that wraps the [`claude_code_sdk`](https://github.com/anthropics/claude-code-sdk-python) package for interacting with Anthropic’s [Claude Code CLI](https://github.com/anthropics/claude-code) agentic CLI toolkit based on their Claude models.

**Key Responsibilities:**

- Claude API integration
- Session management and persistence
- Tool approval strategies
- Response caching
- Session branching/merging

**Development Focus:**

- Maintain claude-code-sdk compatibility
- Enhance session features
- Improve approval strategies
- Optimize caching logic

### 2.3. `claif_cod`:Claif provider for the OpenAI Codex CLI toolkit

[`claif_cod`](https://github.com/twardoch/claif_cod/): CLI and Python package for interacting with OpenAI’s new [Codex CLI](https://github.com/openai/codex) agentic CLI toolkit based on OpenAI’s models.

**Key Responsibilities:**

- Code generation and manipulation
- Action mode management (review/interactive/auto)
- Working directory integration
- Project-aware operations

**Development Focus:**

- Code safety and review features
- File system operations
- Project context awareness
- Action mode refinement

## 3. Working Principles forClaif Development

### 3.1. Core Development Principles

When developing forClaif (in any sub-project):

- **Iterate gradually**, avoiding major breaking changes to the plugin interface
- **Minimize user confirmations** while maintaining safety, especially for code operations
- **Preserve existing API contracts** unless a major version bump is planned
- **Use module-level constants** over magic numbers (e.g., `DEFAULT_TIMEOUT = 120`)
- **Check for existing utilities** in `claif.common` before implementing new ones
- **Ensure coherence** between provider implementations and the unified interface
- **Focus on minimal viable features** and ship incremental improvements
- **Write comprehensive docstrings** explaining both what and WHY, including cross-references
- **Analyze provider differences** line-by-line when implementing unified features
- **Handle provider failures gracefully** with retries, fallbacks, and clear error messages
- **Address edge cases** like network timeouts, API limits, and malformed responses
- **Let the framework handle complexity**, minimize provider-specific user decisions
- **Reduce cognitive load** through consistent naming and behavior across providers
- **Modularize provider logic** into focused, testable components
- **Favor flat provider hierarchies** over deeply nested inheritance
- **Maintain documentation**:
  - README.md (purpose and usage for each sub-project)
  - CHANGELOG.md (version history with migration notes)
  - TODO.md (planned features and known issues)
  - PROGRESS.md (implementation status for each provider)

### 3.2. Using Development Tools

Before and during development, you should:

- Use `context7` tool to check latest Python package documentation
- Consult `deepseek/deepseek-r1-0528:free` via `chat_completion` for complex architectural decisions
- Query `openai/o3` via `chat_completion` for API design and compatibility questions
- Apply `sequentialthinking` tool for solving cross-provider compatibility issues
- Search with `perplexity_ask` and `duckduckgo_web_search` for provider API updates

### 3.3. File Organization

In each source file, maintain the `this_file` record:

```python
# this_file: src/claif_cla/cli.py
"""CLI interface for the Claif Claude provider"""
```

### 3.4. Python-Specific Guidelines

For allClaif Python code:

- **PEP 8**: Consistent formatting with 120-char line limit (per pyproject.toml)
- **Descriptive names**: `query_with_retry()` not `qwr()`
- **PEP 20**: Explicit provider selection over magic
- **Type hints**: Use simple unions (`str | None` not `Optional[str]`)
- **PEP 257**: Imperative mood docstrings with provider examples
- **Modern Python**: f-strings, pattern matching for message types
- **Logging**: Loguru-based with provider-specific contexts
- **CLI scripts**: Fire & rich with uv shebang:

```python
#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "claif"]
# ///
# this_file: scripts/provider_test.py
```

After changes, run:

```bash
uv run uzpy run .
fd -e py -x autoflake {}
fd -e py -x pyupgrade --py312-plus {}
fd -e py -x ruff check --output-format=github --fix --unsafe-fixes {}
fd -e py -x ruff format --respect-gitignore --target-version py312 {}
python -m pytest
```

## 4. Sub-Project Specific Guidelines

### 4.1. `claif_gem`:Claif provider for the Google Gemini CLI toolkit

**Subprocess Management:**

- Use anyio subprocess with proper cleanup (IMPLEMENTED)
- Implement timeout handling for long-running queries (IMPLEMENTED)
- Handle CLI output parsing robustly (IMPLEMENTED - JSON and plain text)

**Configuration:**

- Support environment variables (IMPLEMENTED - GEMINI_CLI_PATH)
- Validate CLI path existence with multiple search locations (IMPLEMENTED)
- Cache model availability (TODO)

**Platform Support:**

- Test on Windows, macOS, Linux (IMPLEMENTED - cross-platform CLI discovery)
- Handle path separators correctly (IMPLEMENTED - using pathlib)
- Support different Gemini CLI versions (IMPLEMENTED - flexible argument parsing)


## 5. Quality Assurance

### 5.1. Pre-Commit Checks

All sub-projects must pass:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  hooks:
    - id: ruff
    - id: ruff-format
- repo: https://github.com/pre-commit/mirrors-mypy
  hooks:
    - id: mypy
```

### 5.2. Testing Strategy

1. **Unit Tests**: Provider-specific logic
2. **Integration Tests**: Provider +Claif core
3. **E2E Tests**: CLI commands with real providers
4. **Performance Tests**: Response time, memory usage

### 5.3. Documentation Requirements

Each sub-project must maintain:

- Comprehensive README with examples
- API reference (autodoc where possible)
- Migration guides for breaking changes
- Troubleshooting section

## 6. Virtual Team Collaboration

When developingClaif:

**Be creative, diligent, critical, relentless & funny!**

Lead two virtual experts:

- **"Ideot"**: Proposes creative provider features and unconventional integrations
- **"Critin"**: Critiques API design and identifies compatibility issues

The three of you shall:

- Illuminate the best provider abstraction patterns
- Process provider differences methodically
- Collaborate on cross-provider features
- Adapt when provider APIs change

If compatibility issues arise, step back and focus on the unified interface goals.

## 7. Release Coordination

SinceClaif uses a monorepo structure:

1. Version all packages together
2. Update inter-package dependencies
3. Test all providers before release
4. Publish in order: claif → providers
5. Tag releases with `v{version}`

## 8. Final Checkpoint

When completing anyClaif development:

**"Wait, but..."** - Review your changes:

- Does it maintain provider abstraction?
- Is the API still unified?
- Are errors handled consistently?
- Is the documentation updated?

Repeat this reflection, but stick to "minimal viable next version" philosophy.

Remember:Claif's strength is its unified interface. Every line of code should serve this goal while allowing providers to shine with their unique capabilities.
