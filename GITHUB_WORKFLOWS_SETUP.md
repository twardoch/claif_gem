# GitHub Workflows Setup Instructions

Due to GitHub App permissions, the workflow files need to be manually created in the `.github/workflows/` directory. This document provides the complete setup instructions.

## Quick Setup

1. Create the `.github/workflows/` directory in your repository
2. Copy the workflow files from the `github-workflows/` directory to `.github/workflows/`
3. Commit and push the changes

```bash
# Create the directory
mkdir -p .github/workflows

# Copy the workflow files
cp github-workflows/binaries.yml .github/workflows/

# Commit the changes
git add .github/workflows/
git commit -m "Add GitHub Actions workflows for multiplatform binary builds"
git push
```

## Workflow Files

### 1. Enhanced CI Workflow (`.github/workflows/ci.yml`)

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]
        
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v4
      with:
        version: "latest"
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        uv venv
        uv pip install -e ".[test,dev]"
    
    - name: Run linting
      run: |
        uv run ruff check src/claif_gem tests/
        uv run ruff format --check src/claif_gem tests/
    
    - name: Run type checking
      run: |
        uv run mypy src/claif_gem
    
    - name: Run tests
      run: |
        uv run pytest tests/ -v --tb=short --cov=claif_gem --cov-report=xml
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v4
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.12'
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: false

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v4
      with:
        version: "latest"
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    
    - name: Install dependencies
      run: |
        uv venv
        uv pip install -e ".[test,dev]"
        uv pip install bandit safety
    
    - name: Run security checks
      run: |
        uv run bandit -r src/claif_gem/ -f json -o bandit-report.json || true
        uv run safety check --json --output safety-report.json || true
    
    - name: Upload security reports
      uses: actions/upload-artifact@v4
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
```

### 2. Enhanced Release Workflow

Add this to your existing `.github/workflows/release.yml` in the release job:

```yaml
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
          generate_release_notes: true
          body: |
            ## Installation
            
            ### Python Package
            ```bash
            pip install claif-gem
            ```
            
            ### Binary Installation
            Pre-compiled binaries are available in the assets below for Linux, Windows, and macOS.
            
            1. Download the appropriate binary for your platform
            2. Extract the archive 
            3. Move the binary to a directory in your PATH
            4. Make it executable (Linux/macOS): `chmod +x claif-gem`
            5. Run: `claif-gem --help`
            
            **Note**: Binary builds are triggered automatically after this release completes.
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 3. Binary Build Workflow

The complete binary build workflow is in `github-workflows/binaries.yml`. Copy this file to `.github/workflows/binaries.yml`.

## Required GitHub Secrets

For the workflows to function properly, you'll need these secrets in your GitHub repository:

### Repository Secrets
- `PYPI_TOKEN`: PyPI API token for publishing packages
- `TEST_PYPI_TOKEN`: TestPyPI API token for testing releases

### Optional Secrets
- `CODECOV_TOKEN`: For coverage reporting (optional)

## Setting Up Secrets

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets and variables → Actions
3. Add the required secrets:

```bash
# Get PyPI token from https://pypi.org/manage/account/token/
PYPI_TOKEN=pypi-...

# Get TestPyPI token from https://test.pypi.org/manage/account/token/
TEST_PYPI_TOKEN=pypi-...
```

## Testing the Workflows

### Test CI Pipeline
```bash
# Create a test branch and push
git checkout -b test-workflows
git push -u origin test-workflows
```

### Test Release Pipeline
```bash
# Create a test release
./scripts/release.sh 1.0.29 --dry-run  # Test first
./scripts/release.sh 1.0.29            # Create actual release
```

## Workflow Triggers

- **CI**: Runs on every push to main and all pull requests
- **Release**: Runs when you push a git tag (e.g., `v1.0.29`)
- **Binaries**: Runs after successful releases and can be triggered manually

## Expected Workflow Results

After setting up the workflows, you'll get:

1. **Automated Testing**: Every commit is tested on 3 platforms × 3 Python versions
2. **Automated Releases**: Tag push triggers complete release process
3. **Binary Builds**: Standalone executables for Linux, Windows, macOS
4. **PyPI Publishing**: Automatic package publishing to PyPI
5. **GitHub Releases**: Automatic release creation with assets

## Troubleshooting

### Common Issues

1. **Workflow not triggering**: Check that files are in `.github/workflows/` directory
2. **Permission errors**: Ensure GitHub App has proper permissions
3. **Secret errors**: Verify all required secrets are set
4. **Binary build failures**: Check PyInstaller configuration

### Manual Workflow Triggers

You can manually trigger workflows from the GitHub Actions tab:
1. Go to Actions tab in your repository
2. Select the workflow
3. Click "Run workflow" button

## File Structure After Setup

```
claif_gem/
├── .github/
│   └── workflows/
│       ├── ci.yml           # Enhanced CI pipeline
│       ├── release.yml      # Enhanced release pipeline
│       └── binaries.yml     # Binary build pipeline
├── github-workflows/        # Template files (can be deleted after setup)
│   └── binaries.yml
├── scripts/                 # Local development scripts
└── ...
```

## Next Steps

1. Set up the GitHub workflows as described above
2. Configure the required secrets
3. Test the CI pipeline with a pull request
4. Test the release pipeline with a version tag
5. Verify binary builds are working correctly

The complete release system will then be fully operational!