# Release Guide

This document describes the release process for claif_gem, which uses git-tag-based semantic versioning.

## Overview

The project uses:
- **Git tags** for version control (semantic versioning: `vX.Y.Z`)
- **hatch-vcs** for automatic version generation from git tags
- **GitHub Actions** for automated CI/CD pipeline
- **Local scripts** for manual testing and releases

## Version Management

### Current Version
The current version is automatically derived from git tags and development commits:
- Tagged releases: `1.0.28` (from tag `v1.0.28`)
- Development versions: `1.0.29.dev7+g6c31860.d20250717` (7 commits after `v1.0.28`)

### Version Sources
1. **Git tags**: Official releases (e.g., `v1.0.28`)
2. **Development commits**: Automatic dev versions between tags
3. **Fallback**: `0.1.0-dev` if no git history available

## Local Development

### Prerequisites
- Python 3.10+
- uv package manager
- Git

### Setup
```bash
# Install uv if not available
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev,test]"
```

### Available Scripts

#### 1. Test Script
```bash
# Run full test suite with linting and type checking
./scripts/test.sh

# Run with coverage
./scripts/test.sh --coverage

# Run in parallel
./scripts/test.sh --parallel

# Quick test (skip linting, focus on core functionality)
./scripts/quick-test.sh
```

#### 2. Build Script
```bash
# Build wheel and source distribution
./scripts/build.sh
```

#### 3. Release Script
```bash
# Create a new release
./scripts/release.sh 1.0.29

# Dry run (show what would happen)
./scripts/release.sh 1.0.29 --dry-run

# Skip tests (not recommended)
./scripts/release.sh 1.0.29 --skip-tests

# Skip build
./scripts/release.sh 1.0.29 --skip-build
```

## Release Process

### 1. Prepare Release

1. Ensure you're on the `main` branch
2. Make sure all changes are committed
3. Run tests to ensure everything works:
   ```bash
   ./scripts/test.sh
   ```

### 2. Create Release

Use the release script:
```bash
./scripts/release.sh 1.0.29
```

This will:
1. Validate the version format
2. Check working directory is clean
3. Pull latest changes
4. Run tests
5. Build the package
6. Create and push git tag
7. Trigger GitHub Actions

### 3. Monitor GitHub Actions

After pushing the tag, GitHub Actions will:
1. **CI Pipeline**: Run tests on multiple platforms/Python versions
2. **Release Pipeline**: 
   - Test on TestPyPI first
   - Build multiplatform binaries
   - Create GitHub release
   - Publish to PyPI
   - Upload binary artifacts

### 4. Verify Release

1. Check GitHub release page
2. Verify PyPI package
3. Test binary downloads
4. Update documentation if needed

## GitHub Actions

### CI Workflow (`.github/workflows/ci.yml`)
- **Triggers**: Push to main, PRs
- **Platforms**: Ubuntu, Windows, macOS
- **Python versions**: 3.10, 3.11, 3.12
- **Steps**: Install, lint, type check, test, coverage, security

### Release Workflow (`.github/workflows/release.yml`)
- **Triggers**: Git tags (`v*`)
- **Steps**: Test, build, TestPyPI, PyPI, GitHub release

### Binary Build Workflow (`.github/workflows/binaries.yml`)
- **Triggers**: Git tags, manual dispatch, after release
- **Platforms**: Linux, Windows, macOS
- **Output**: Standalone executables via PyInstaller

## Binary Builds

### Supported Platforms
- Linux (x86_64): `claif-gem-linux-amd64.tar.gz`
- Windows (x86_64): `claif-gem-windows-amd64.zip`
- macOS (x86_64): `claif-gem-macos-amd64.tar.gz`

### Manual Binary Build
```bash
# Install PyInstaller
uv pip install pyinstaller

# Build binary
uv run pyinstaller claif-gem.spec

# Test binary
./dist/claif-gem --help
```

## Troubleshooting

### Common Issues

1. **Version not updating**: Make sure you've created and pushed the git tag
2. **Tests failing**: Check the specific test output and fix issues before release
3. **Build failing**: Ensure all dependencies are properly specified
4. **Binary build failing**: Check PyInstaller configuration and hidden imports

### Manual Recovery

If GitHub Actions fail, you can:
1. Fix the issue locally
2. Delete the problematic tag: `git tag -d v1.0.29 && git push origin :v1.0.29`
3. Re-run the release script
4. Or manually trigger workflows from GitHub interface

## Configuration

### Environment Variables
- `GEMINI_CLI_PATH`: Path to Gemini CLI executable
- `GEMINI_API_KEY`: API key for Gemini (for testing)

### GitHub Secrets
- `PYPI_TOKEN`: PyPI API token for publishing
- `TEST_PYPI_TOKEN`: TestPyPI API token for testing

## Best Practices

1. **Always test before release**: Run `./scripts/test.sh` first
2. **Use semantic versioning**: Follow `MAJOR.MINOR.PATCH` format
3. **Keep changelog updated**: Document changes in `CHANGELOG.md`
4. **Test on multiple platforms**: Use GitHub Actions matrix
5. **Verify releases**: Check PyPI and GitHub releases after deployment

## Version History

Current version scheme:
- `1.0.x`: Stable releases
- `1.0.x.devN+gHASH`: Development versions
- `vX.Y.Z`: Git tags for releases

See `git tag -l` for all available versions.