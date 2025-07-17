#!/bin/bash
# this_file: scripts/release.sh
# Release script for claif_gem package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[RELEASE]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Usage function
usage() {
    echo "Usage: $0 <version> [--dry-run] [--skip-tests] [--skip-build]"
    echo "  version: Semantic version (e.g., 1.2.3)"
    echo "  --dry-run: Show what would be done without actually doing it"
    echo "  --skip-tests: Skip running tests"
    echo "  --skip-build: Skip building the package"
    echo ""
    echo "Examples:"
    echo "  $0 1.2.3                 # Normal release"
    echo "  $0 1.2.3 --dry-run       # Show what would happen"
    echo "  $0 1.2.3 --skip-tests    # Skip tests (not recommended)"
    exit 1
}

# Parse arguments
VERSION=""
DRY_RUN=false
SKIP_TESTS=false
SKIP_BUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            if [[ -z "$VERSION" ]]; then
                VERSION="$1"
            else
                print_error "Unknown option: $1"
                usage
            fi
            shift
            ;;
    esac
done

# Validate version
if [[ -z "$VERSION" ]]; then
    print_error "Version is required"
    usage
fi

# Validate semantic version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Version must be in semantic version format (e.g., 1.2.3)"
    exit 1
fi

# Ensure we're in the right directory
cd "$(dirname "${BASH_SOURCE[0]}")/.."

print_status "Starting release process for version $VERSION..."

if [[ "$DRY_RUN" == true ]]; then
    print_warning "DRY RUN MODE - No actual changes will be made"
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Set up PATH for uv
export PATH="$HOME/.local/bin:$PATH"

# Check if we're in a git repository
if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    print_error "Not in a git repository"
    exit 1
fi

# Check if working directory is clean
if [[ $(git status --porcelain) ]]; then
    print_error "Working directory is not clean. Please commit your changes first."
    git status --short
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" ]]; then
    print_warning "Current branch is '$CURRENT_BRANCH', not 'main'"
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if tag already exists
if git tag -l | grep -q "^v$VERSION$"; then
    print_error "Tag v$VERSION already exists"
    exit 1
fi

# Pull latest changes
print_status "Pulling latest changes..."
if [[ "$DRY_RUN" == false ]]; then
    git pull origin "$CURRENT_BRANCH"
fi

# Run tests unless skipped
if [[ "$SKIP_TESTS" == false ]]; then
    print_status "Running tests..."
    if [[ "$DRY_RUN" == false ]]; then
        ./scripts/test.sh
    else
        print_info "Would run: ./scripts/test.sh"
    fi
fi

# Build package unless skipped
if [[ "$SKIP_BUILD" == false ]]; then
    print_status "Building package..."
    if [[ "$DRY_RUN" == false ]]; then
        ./scripts/build.sh
    else
        print_info "Would run: ./scripts/build.sh"
    fi
fi

# Create and push tag
print_status "Creating and pushing tag v$VERSION..."
if [[ "$DRY_RUN" == false ]]; then
    git tag -a "v$VERSION" -m "Release version $VERSION"
    git push origin "v$VERSION"
else
    print_info "Would create tag: v$VERSION"
    print_info "Would push tag to origin"
fi

# Show what happens next
print_status "Release process completed!"
print_info "Tag v$VERSION has been created and pushed."
print_info "GitHub Actions will now:"
print_info "  1. Run the full test suite"
print_info "  2. Build multiplatform binaries"
print_info "  3. Create a GitHub release"
print_info "  4. Publish to PyPI (if configured)"

if [[ "$DRY_RUN" == false ]]; then
    print_info "You can monitor the progress at:"
    print_info "  https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:\/]\([^\/]*\/[^\/]*\).*/\1/' | sed 's/\.git$//')/actions"
fi