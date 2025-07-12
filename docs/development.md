# Development Guide

Guide for contributing to and developing XC8 Wrapper.

## Quick Reference

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=xc8_wrapper

# Format and lint code
ruff check --fix .
ruff format .

# Type checking
mypy .

# Build package
python -m build
```

## Getting Started with Development

### Prerequisites

- **Python 3.9+**
- **Git** for version control
- **XC8 Compiler** for testing (optional but recommended)

### Setting Up the Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/s-celles/xc8-wrapper.git
   cd xc8-wrapper
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv

   # On Windows
   .venv\Scripts\activate

   # On Linux/macOS
   source .venv/bin/activate
   ```

3. **Install in development mode:**
   ```bash
   pip install -e .[dev]
   ```

4. **Install pre-commit hooks:**
   ```bash
   pre-commit install
   ```

### Verifying Your Setup

```bash
# Run the test suite
pytest

# Check code formatting and linting
ruff check .
ruff format --check .

# Check type annotations
mypy .

# Run security checks
bandit -r xc8_wrapper/

# Run all pre-commit hooks
pre-commit run --all-files
```

## Project Structure

```
xc8-wrapper/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
├── docs/                   # Documentation (Jekyll)
├── tests/                  # Test suite
│   ├── test_cli.py        # CLI interface tests
│   ├── test_core.py       # Core functionality tests
│   ├── test_integration.py # Integration tests
│   └── ...
├── xc8_wrapper/           # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   └── core.py            # Core functionality
├── pyproject.toml         # Project configuration
├── README.md              # Main project README
└── requirements files...
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

Follow these guidelines:
- Write clean, readable code
- Add type annotations to all functions
- Follow the existing code style
- Write tests for new functionality
- Update documentation as needed

### 3. Run Tests and Checks

```bash
# Run tests
pytest -v

# Run tests with coverage
pytest --cov=xc8_wrapper --cov-report=html

# Format and lint code
ruff check --fix .
ruff format .

# Check types
mypy .

# Check security
bandit -r xc8_wrapper/
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature description"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring
- `style:` for formatting changes
- `ci:` for CI/CD changes

### 5. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xc8_wrapper --cov-report=term-missing

# Run specific test file
pytest tests/test_core.py -v

# Run tests matching a pattern
pytest -k "test_xc8_detection" -v

# Run tests in parallel
pytest -n auto
```

### Test Categories

We use pytest markers to categorize tests:

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# CLI tests only
pytest -m cli
```

### Writing Tests

When adding new functionality, always include tests:

```python
import pytest
from unittest.mock import patch, MagicMock
from xc8_wrapper.core import get_xc8_tool_path

def test_get_xc8_tool_path_success():
    """Test successful XC8 tool path detection."""
    with patch('pathlib.Path.exists', return_value=True):
        result = get_xc8_tool_path('cc', '3.00')
        assert result is not None
        assert 'xc8-cc' in str(result)

def test_get_xc8_tool_path_not_found():
    """Test XC8 tool path when not found."""
    with patch('pathlib.Path.exists', return_value=False):
        result = get_xc8_tool_path('cc', '3.00')
        assert result is None
```

### Mock Guidelines

- Mock external dependencies (file system, subprocess calls)
- Use `pathlib.Path` mocking for cross-platform tests
- Mock XC8 executables for CI environments where XC8 isn't installed

## Code Quality

### Code Style

We use several tools to maintain code quality:

- **Ruff**: Code formatting, import sorting, and linting
- **mypy**: Type checking
- **bandit**: Security scanning

### Type Annotations

All functions must have type annotations:

```python
from pathlib import Path
from typing import Optional, List

def get_xc8_tool_path(tool: str, version: str) -> Optional[Path]:
    """Get the path to an XC8 tool executable."""
    # Implementation here
    pass

def run_command(args: List[str], cwd: Optional[Path] = None) -> int:
    """Run a command and return the exit code."""
    # Implementation here
    pass
```

### Documentation Strings

Use clear docstrings with examples:

```python
def compile_project(cpu: str, xc8_version: str, **kwargs) -> bool:
    """
    Compile a PIC project using XC8.

    Args:
        cpu: Target microcontroller (e.g., 'PIC16F877A')
        xc8_version: XC8 version to use (e.g., '3.00')
        **kwargs: Additional compilation options

    Returns:
        True if compilation succeeded, False otherwise

    Raises:
        FileNotFoundError: If XC8 compiler is not found
        ValueError: If invalid parameters are provided

    Example:
        >>> compile_project('PIC16F877A', '3.00', optimization='-O2')
        True
    """
    # Implementation here
    pass
```

## Architecture

### Core Design Principles

1. **Security First**: All inputs are validated and sanitized
2. **Cross-Platform**: Use `pathlib` for all path operations
3. **Testable**: Functions are pure and mockable where possible
4. **User-Friendly**: Clear error messages and helpful defaults

### Key Components

**CLI Module (`cli.py`)**
- Command-line argument parsing
- User input validation
- Error handling and user feedback

**Core Module (`core.py`)**
- XC8 detection logic
- Compilation orchestration
- File system operations

### Adding New Features

When adding new features:

1. **Start with tests** - Write failing tests first
2. **Implement core logic** - Add to `core.py`
3. **Add CLI interface** - Update `cli.py` if needed
4. **Update documentation** - Add to relevant docs
5. **Update CLI reference** - Document new options

## Continuous Integration

### GitHub Actions

We use GitHub Actions for CI/CD:

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.9, 3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: pip install -e .[dev]
    - name: Run tests
      run: pytest --cov=xc8_wrapper
```

### Quality Gates

All pull requests must pass:
- ✅ All tests on all platforms and Python versions
- ✅ Code coverage ≥ 78%
- ✅ Code formatting and linting (ruff)
- ✅ Type checking (mypy)
- ✅ Security scanning (bandit)

## Documentation

### Building Documentation Locally

The documentation uses Jekyll and is deployed to GitHub Pages:

```bash
# Install Jekyll (requires Ruby)
cd docs
bundle install

# Serve locally
bundle exec jekyll serve

# Build static site
bundle exec jekyll build
```

### Documentation Structure

- `docs/index.md` - Main landing page
- `docs/installation.md` - Installation instructions
- `docs/getting-started.md` - Tutorial
- `docs/cli-reference.md` - Complete CLI documentation
- `docs/examples.md` - Usage examples
- `docs/faq.md` - Frequently asked questions
- `docs/development.md` - This development guide

### Writing Documentation

- Use clear, concise language
- Include practical examples
- Test all code examples
- Use consistent formatting

## Release Process

### Version Management

We use semantic versioning (semver):
- **Major** (1.0.0): Breaking changes
- **Minor** (0.1.0): New features, backward compatible
- **Patch** (0.0.1): Bug fixes, backward compatible

### Creating a Release

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Create a git tag:**
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```
4. **GitHub Actions** will automatically build and publish to PyPI

## Contributing Guidelines

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Ensure all checks pass
6. Submit a pull request

### Code Review

All changes require code review:
- At least one approving review
- All CI checks must pass
- Address reviewer feedback promptly

### Communication

- Use GitHub Issues for bug reports and feature requests
- Use GitHub Discussions for questions and ideas
- Be respectful and constructive in all interactions

## Usage Examples

After installation, you can use the wrapper in multiple ways:

```bash
# Command-line tool
xc8-wrapper --cpu PIC16F876A --xc8-version 3.00

# Python module
python -m xc8_wrapper.cli --cpu PIC16F876A --xc8-version 3.00

# Python API
from xc8_wrapper import get_xc8_tool_path, handle_cc_tool
```

## Getting Help

- 📚 Read the documentation
- 🔍 Search existing issues
- 💬 Start a discussion
- 📧 Contact maintainers

Thank you for contributing to XC8 Wrapper! 🚀
