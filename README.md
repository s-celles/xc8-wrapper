# XC8 Wrapper

[![CI](https://github.com/s-celles/xc8-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/s-celles/xc8-wrapper/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/s-celles/xc8-wrapper/branch/main/graph/badge.svg)](https://codecov.io/gh/s-celles/xc8-wrapper)
[![PyPI version](https://badge.fury.io/py/xc8-wrapper.svg)](https://badge.fury.io/py/xc8-wrapper)
[![Python versions](https://img.shields.io/pypi/pyversions/xc8-wrapper.svg)](https://pypi.org/project/xc8-wrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python wrapper for Microchip's XC8 toolchain for PIC microcontrollers.

## Installation

```bash
pip install xc8-wrapper
```

## Usage

```bash
# Basic compilation
xc8-wrapper --cpu PIC16F876A --xc8-version 3.00

# With optimization
xc8-wrapper --cpu PIC16F876A --xc8-version 3.00 -O2

# With custom source and build directories
xc8-wrapper --cpu PIC16F876A --xc8-version 3.00 --source-dir my_src --build-dir my_build
```

## Features

- Complete wrapper around xc8-cc.exe
- Support for all XC8 compiler flags
- Colored output for better readability
- Flexible configuration options
- Cross-platform support (Windows, Linux, macOS)

## Requirements

- Python 3.8+
- Microchip XC8 Compiler installed
- colorama package (installed automatically)

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/xc8-wrapper.git
cd xc8-wrapper

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=xc8_wrapper --cov-report=term-missing

# Run quick tests
python run_tests.py

# Format code
black .

# Type checking
mypy .

# Run all linting
flake8 xc8_wrapper tests

# Run pre-commit hooks
pre-commit run --all-files
```

## Testing

The package includes comprehensive test coverage:

### Quick Testing
```bash
# Run the quick test script
python run_tests.py
```

### Detailed Testing
```bash
# Run all tests with coverage
pytest --cov=xc8_wrapper --cov-report=html

# Run specific test categories
pytest tests/test_core.py -v
pytest tests/test_cli.py -v
pytest tests/test_integration.py -v

# Run tests in parallel
pytest -n auto

# Run tests with specific markers
pytest -m "unit" -v
pytest -m "integration" -v
```

### Continuous Integration
This project uses GitHub Actions for CI/CD:

- **Automated Testing**: Tests run on Python 3.8-3.12 across Windows, macOS, and Linux
- **Code Quality**: Automatic linting, formatting, and type checking
- **Security**: Dependency vulnerability scanning
- **Coverage**: Code coverage reporting with Codecov integration

### Test Structure
```
tests/
├── test_core.py          # Core functionality tests
├── test_cli.py           # CLI interface tests
├── test_integration.py   # Integration tests
└── test_utils.py         # Utility and edge case tests
```

### Pre-commit Hooks
Set up pre-commit hooks for development:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

## Important Legal Notice

**This package is a wrapper for Microchip's proprietary XC8 compiler tools.**

### What This Package Provides
This package provides Python wrapper code that interfaces with Microchip's XC8 compiler tools. It does NOT include the actual XC8 compiler software.

### Microchip XC8 Compiler License
The XC8 compiler tools (`xc8-cc.exe`, `xc8-ld.exe`, etc.) are **proprietary software owned exclusively by Microchip Technology Inc.** and are subject to Microchip's own license terms. You must:

1. **Download and install** the XC8 compiler from Microchip's official website
2. **Obtain proper licenses** from Microchip to use the XC8 tools
3. **Comply with Microchip's license terms** for the XC8 compiler

### This Package's License
The Python wrapper code in this package is released under the **MIT License** (see LICENSE file).

### Your Responsibility
**You are responsible for obtaining proper licenses for the Microchip XC8 compiler tools that this wrapper interfaces with.**

For more information about XC8 licensing, visit:
- [Microchip XC8 Compiler](https://www.microchip.com/en-us/tools-resources/develop/mplab-xc-compilers)
- [Microchip License Terms](https://www.microchip.com/en-us/legal/terms-of-use)

## License

**Wrapper Code**: MIT License (see LICENSE file)
**Microchip XC8 Tools**: Proprietary Microchip licenses (separate licensing required)
