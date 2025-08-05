# Contributing Guide

Welcome to `claif_gem`! This guide covers everything you need to know to contribute to the project, from setting up your development environment to submitting pull requests.

## 🤝 Welcome Contributors

We welcome contributions of all types:

- 🐛 **Bug Reports** - Help us identify and fix issues
- 🚀 **Feature Requests** - Suggest new functionality
- 📖 **Documentation** - Improve guides and examples
- 🧪 **Tests** - Add test coverage and scenarios
- 💻 **Code** - Fix bugs and implement features
- 🎨 **Design** - Improve UX and interfaces
- 🌍 **Translation** - Localization support

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.12+** installed
- **Git** for version control
- **Node.js 18+** or **Bun** for Gemini CLI
- A **Google API key** for testing (optional)
- **GitHub account** for pull requests

### Development Setup

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/your-username/claif_gem.git
cd claif_gem

# Add upstream remote
git remote add upstream https://github.com/twardoch/claif_gem.git
```

#### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install in development mode with all dependencies
pip install -e ".[dev,test,docs]"

# Or using uv (faster)
pip install uv
uv pip install -e ".[dev,test,docs]"
```

#### 3. Install Gemini CLI

```bash
# Using npm
npm install -g @google/gemini-cli

# Or using Bun (recommended)
curl -fsSL https://bun.sh/install | bash
bun add -g @google/gemini-cli
```

#### 4. Set Up Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Test the hooks
pre-commit run --all-files
```

#### 5. Verify Setup

```bash
# Run tests to verify setup
pytest tests/unit -v

# Check code quality
ruff check src/claif_gem tests
ruff format --check src/claif_gem tests

# Type checking
mypy src/claif_gem
```

## 🏗️ Development Workflow

### Branch Strategy

We use a GitHub Flow approach:

1. **main** - Production-ready code
2. **feature/your-feature** - Feature development
3. **fix/issue-description** - Bug fixes
4. **docs/topic** - Documentation updates

### Creating a Feature Branch

```bash
# Ensure you're on main and up to date
git checkout main
git pull upstream main

# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Work on your changes...

# Push to your fork
git push origin feature/your-feature-name
```

### Making Changes

#### Code Style

We use strict code formatting and linting:

```bash
# Format code
ruff format src/claif_gem tests

# Fix linting issues
ruff check --fix src/claif_gem tests

# Check types
mypy src/claif_gem

# Run all checks
pre-commit run --all-files
```

#### Code Standards

1. **PEP 8 Compliance** - Follow Python style guidelines
2. **Type Hints** - Add type hints to all functions and methods
3. **Docstrings** - Use clear, descriptive docstrings
4. **Error Handling** - Handle errors gracefully with custom exceptions
5. **Testing** - Write tests for all new functionality

#### Example Code Structure

```python
# this_file: src/claif_gem/new_module.py
"""Module for new functionality."""

from typing import Any, Optional
from claif_gem.exceptions import GeminiError

def new_function(param: str, optional_param: Optional[int] = None) -> dict[str, Any]:
    """Perform some new functionality.
    
    Args:
        param: Required string parameter
        optional_param: Optional integer parameter
        
    Returns:
        Dictionary containing results
        
    Raises:
        GeminiError: If operation fails
        ValueError: If parameters are invalid
        
    Example:
        >>> result = new_function("test")
        >>> assert "status" in result
    """
    if not param:
        raise ValueError("param cannot be empty")
    
    try:
        # Implementation here
        return {"status": "success", "data": param}
    except Exception as e:
        raise GeminiError(f"Operation failed: {e}") from e
```

### Testing Your Changes

#### Running Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit -v          # Unit tests only
pytest tests/integration -v   # Integration tests
pytest -m "not slow" -v      # Skip slow tests

# Run with coverage
pytest --cov=src/claif_gem --cov-report=html
```

#### Writing Tests

Every new feature should include tests:

```python
# tests/unit/test_new_module.py
"""Tests for new module functionality."""

import pytest
from claif_gem.new_module import new_function
from claif_gem.exceptions import GeminiError

class TestNewFunction:
    """Test suite for new_function."""
    
    def test_basic_functionality(self):
        """Test basic function operation."""
        result = new_function("test")
        assert result["status"] == "success"
        assert result["data"] == "test"
    
    def test_empty_param_raises_error(self):
        """Test that empty param raises ValueError."""
        with pytest.raises(ValueError, match="param cannot be empty"):
            new_function("")
    
    def test_optional_parameter(self):
        """Test function with optional parameter."""
        result = new_function("test", 42)
        assert result["status"] == "success"
    
    @pytest.mark.parametrize("param,expected", [
        ("hello", "hello"),
        ("test123", "test123"),
        ("special!@#", "special!@#"),
    ])
    def test_various_inputs(self, param, expected):
        """Test function with various input values."""
        result = new_function(param)
        assert result["data"] == expected
```

## 📝 Documentation

### Documentation Standards

1. **Docstrings** - Follow Google or NumPy style
2. **Type Hints** - Complete type annotations
3. **Examples** - Include usage examples
4. **API Reference** - Update API documentation
5. **User Guides** - Update relevant guides

### Building Documentation

```bash
# Build documentation locally
cd src_docs
mkdocs serve

# Open http://localhost:8000 to view

# Build static documentation
mkdocs build
```

### Documentation Structure

```
src_docs/
├── mkdocs.yml           # MkDocs configuration
├── md/                  # Markdown content
│   ├── index.md        # Main page
│   ├── quickstart.md   # Getting started
│   ├── usage.md        # Usage examples
│   ├── api-reference.md # API documentation
│   └── ...             # Other guides
└── stylesheets/        # Custom CSS
```

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues** - Check if already reported
2. **Update to latest version** - Ensure bug still exists
3. **Check documentation** - Verify expected behavior
4. **Minimal reproduction** - Create simple test case

### Bug Report Template

```markdown
## Bug Description
Brief description of the issue.

## Environment
- claif_gem version: 
- Python version:
- Operating System:
- Gemini CLI version:

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should have happened.

## Actual Behavior
What actually happened.

## Minimal Code Example
```python
# Code that reproduces the issue
from claif_gem import GeminiClient
client = GeminiClient()
# ... rest of reproduction code
```

## Additional Context
Any other relevant information, error messages, logs, etc.
```

## 🚀 Feature Requests

### Before Requesting

1. **Check existing issues** - Feature might be planned
2. **Consider alternatives** - Existing functionality might suffice
3. **Community discussion** - Start discussion first
4. **Implementation feasibility** - Consider technical constraints

### Feature Request Template

```markdown
## Feature Description
Clear description of the proposed feature.

## Use Case
Explain why this feature would be useful.

## Proposed Implementation
How you envision this working (if you have ideas).

## Alternatives Considered
Other approaches you've considered.

## Examples
Code examples showing how the feature would be used.

```python
# Example of proposed API
client = GeminiClient()
result = client.new_feature(param="value")
```

## Additional Context
Any other relevant information.
```

## 🔄 Pull Request Process

### Before Submitting

1. **Create an issue** - Discuss changes first (for large features)
2. **Write tests** - Ensure good test coverage
3. **Update documentation** - Include relevant docs
4. **Check CI passes** - All tests and checks must pass
5. **Rebase on main** - Ensure clean git history

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Related Issues
Closes #123, Relates to #456

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented where necessary
- [ ] Documentation updated
- [ ] Tests added or updated
- [ ] All checks pass

## Screenshots/Examples
If applicable, add screenshots or code examples.
```

### Review Process

1. **Automated checks** - All CI checks must pass
2. **Code review** - At least one maintainer review
3. **Testing** - Reviewers may test manually
4. **Documentation review** - Check docs are accurate
5. **Final approval** - Maintainer approval required

## 🏷️ Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** - Incompatible API changes
- **MINOR** - New functionality, backwards compatible
- **PATCH** - Bug fixes, backwards compatible

### Release Workflow

1. **Version bump** - Update version in `__version__.py`
2. **Update CHANGELOG** - Document all changes
3. **Create release PR** - Merge to main
4. **Create git tag** - Tag the release commit
5. **GitHub release** - Create release with notes
6. **PyPI upload** - Automated via GitHub Actions

## 🤝 Community Guidelines

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

1. **Be respectful** - Treat everyone with respect
2. **Be inclusive** - Welcome diverse perspectives
3. **Be collaborative** - Work together constructively
4. **Be patient** - Help newcomers learn
5. **Be constructive** - Provide helpful feedback

### Communication Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General discussion and Q&A
- **Pull Requests** - Code review and collaboration
- **Email** - Direct contact with maintainers

### Recognition

Contributors are recognized through:

- **Contributors file** - Listed in CONTRIBUTORS.md
- **Release notes** - Mentioned in releases
- **GitHub insights** - Visible in repository insights
- **Special thanks** - Called out for significant contributions

## 🔧 Advanced Development

### Architecture Decisions

When making significant changes:

1. **Discuss first** - Open an issue for discussion
2. **Design document** - Write design proposal
3. **Backwards compatibility** - Consider existing users
4. **Performance impact** - Measure and optimize
5. **Documentation** - Update architecture docs

### Performance Considerations

- **Minimize subprocess calls** - Cache where possible
- **Efficient parsing** - Optimize response parsing
- **Memory usage** - Monitor memory consumption
- **Async support** - Consider async patterns
- **Error handling** - Fast-fail for invalid inputs

### Security Guidelines

- **Input validation** - Validate all user inputs
- **Secret handling** - Never log sensitive data
- **Dependency updates** - Keep dependencies current
- **Code scanning** - Use automated security tools
- **Responsible disclosure** - Report security issues privately

## 📚 Resources

### Development Tools

- **Ruff** - Linting and formatting
- **MyPy** - Type checking
- **Pytest** - Testing framework
- **Pre-commit** - Git hooks
- **MkDocs** - Documentation

### Learning Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Semantic Versioning](https://semver.org/)

### Project Structure

```
claif_gem/
├── .github/             # GitHub workflows and templates
├── src/claif_gem/       # Source code
├── tests/              # Test suite
├── src_docs/           # Documentation source
├── docs/               # Built documentation
├── scripts/            # Development scripts
├── pyproject.toml      # Project configuration
├── README.md           # Project overview
├── CHANGELOG.md        # Release history
├── CONTRIBUTORS.md     # Contributor list
└── LICENSE             # MIT license
```

## 🎉 Thank You!

Thank you for contributing to `claif_gem`! Your contributions help make this project better for everyone.

### Recognition

All contributors are listed in [CONTRIBUTORS.md](https://github.com/twardoch/claif_gem/blob/main/CONTRIBUTORS.md) and acknowledged in release notes.

### Getting Help

If you need help:

1. Check the [documentation](index.md)
2. Search [existing issues](https://github.com/twardoch/claif_gem/issues)
3. Start a [discussion](https://github.com/twardoch/claif_gem/discussions)
4. Contact maintainers directly

### Stay Connected

- ⭐ Star the repository
- 👀 Watch for updates
- 🍴 Fork for your own experiments
- 📢 Share with others

---

**Happy Contributing! 🚀**

We look forward to your contributions and appreciate your support in making `claif_gem` even better!