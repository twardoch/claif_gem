#!/bin/bash
# this_file: scripts/demo-release.sh
# Demo script to show the release system capabilities

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_status() {
    echo -e "${GREEN}[DEMO]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

# Ensure we're in the right directory
cd "$(dirname "${BASH_SOURCE[0]}")/.."

print_header "claif_gem Release System Demo"

# Show current version
print_status "Current version information:"
if [ -f "src/claif_gem/__version__.py" ]; then
    VERSION=$(grep "__version__ = " src/claif_gem/__version__.py | cut -d'"' -f2)
    echo "Package version: $VERSION"
else
    echo "Package version: Not available (install package first)"
fi

# Show git information
print_status "Git information:"
echo "Current branch: $(git branch --show-current)"
echo "Latest commit: $(git log --oneline -1)"
echo "Latest tag: $(git describe --tags --abbrev=0 2>/dev/null || echo 'No tags found')"

# Show available scripts
print_header "Available Scripts"
print_info "The following scripts are available for development and release:"
echo "1. ./scripts/test.sh - Run test suite"
echo "2. ./scripts/quick-test.sh - Quick test (skip linting)"
echo "3. ./scripts/build.sh - Build package"
echo "4. ./scripts/release.sh - Create release"

# Show GitHub Actions
print_header "GitHub Actions"
print_info "The following workflows are configured:"
echo "1. CI (.github/workflows/ci.yml) - Continuous Integration"
echo "2. Release (.github/workflows/release.yml) - Release to PyPI"
echo "3. Binaries (.github/workflows/binaries.yml) - Build multiplatform binaries"

# Show package info
print_header "Package Information"
print_info "Current package structure:"
echo "- Source: src/claif_gem/"
echo "- Tests: tests/"
echo "- Scripts: scripts/"
echo "- Documentation: README.md, RELEASE.md"

# Show versioning system
print_header "Versioning System"
print_info "Git-tag-based semantic versioning:"
echo "- Release tags: v1.0.28, v1.0.29, etc."
echo "- Development versions: 1.0.29.dev7+g6c31860"
echo "- Automatic version generation via hatch-vcs"

# Show next steps
print_header "Next Steps"
print_info "To create a new release:"
echo "1. Test: ./scripts/test.sh"
echo "2. Build: ./scripts/build.sh"
echo "3. Release: ./scripts/release.sh 1.0.29"
echo "4. Monitor: GitHub Actions will handle the rest"

print_header "Demo Complete"
print_status "The claif_gem release system is ready for use!"
print_info "See RELEASE.md for detailed instructions"