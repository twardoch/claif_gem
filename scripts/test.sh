#!/bin/bash
# this_file: scripts/test.sh
# Test script for claif_gem package

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[TEST]${NC} $1"
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

# Ensure we're in the right directory
cd "$(dirname "${BASH_SOURCE[0]}")/.."

print_status "Starting test suite..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install it first:"
    print_error "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Set up PATH for uv
export PATH="$HOME/.local/bin:$PATH"

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    print_status "Creating virtual environment..."
    uv venv
fi

if [ ! -f ".venv/pyvenv.cfg" ]; then
    print_status "Installing dependencies..."
    uv pip install -e ".[test,dev]"
fi

# Activate virtual environment
source .venv/bin/activate

# Run code quality checks
print_status "Running code quality checks..."

print_info "Running ruff linting..."
ruff check src/claif_gem tests/ || {
    print_error "Linting failed"
    exit 1
}

print_info "Running ruff formatting check..."
ruff format --check src/claif_gem tests/ || {
    print_error "Code formatting check failed"
    exit 1
}

print_info "Running type checking..."
mypy src/claif_gem || {
    print_error "Type checking failed"
    exit 1
}

# Run tests
print_status "Running test suite..."

# Test options
PYTEST_ARGS="-v --tb=short"

# Add coverage if requested
if [ "${1:-}" = "--coverage" ]; then
    print_info "Running tests with coverage..."
    PYTEST_ARGS="$PYTEST_ARGS --cov=claif_gem --cov-report=term-missing --cov-report=html"
fi

# Add parallel execution if requested
if [ "${1:-}" = "--parallel" ]; then
    print_info "Running tests in parallel..."
    PYTEST_ARGS="$PYTEST_ARGS -n auto"
fi

# Run the tests
python -m pytest $PYTEST_ARGS tests/ || {
    print_error "Tests failed"
    exit 1
}

print_status "All tests passed successfully!"

# Show coverage report if generated
if [ -f htmlcov/index.html ]; then
    print_info "Coverage report generated: htmlcov/index.html"
fi

print_status "Test suite completed successfully!"