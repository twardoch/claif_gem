#!/bin/bash
# this_file: scripts/build.sh
# Build script for claif_gem package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[BUILD]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Ensure we're in the right directory
cd "$(dirname "${BASH_SOURCE[0]}")/.."

print_status "Starting build process..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Set up PATH for uv
export PATH="$HOME/.local/bin:$PATH"

# Clean previous builds
print_status "Cleaning previous builds..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

# Install build dependencies
print_status "Installing build dependencies..."
uv pip install --upgrade build hatch

# Build the package
print_status "Building source distribution..."
uv run hatch build --target sdist

print_status "Building wheel distribution..."
uv run hatch build --target wheel

# Check the build
print_status "Checking build artifacts..."
ls -la dist/

# Verify the package
print_status "Verifying package..."
if [ -f dist/*.whl ]; then
    print_status "✓ Wheel built successfully"
else
    print_error "✗ Wheel build failed"
    exit 1
fi

if [ -f dist/*.tar.gz ]; then
    print_status "✓ Source distribution built successfully"
else
    print_error "✗ Source distribution build failed"
    exit 1
fi

# Show package info
print_status "Package information:"
uv run hatch version

print_status "Build completed successfully!"