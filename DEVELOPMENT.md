# XC8 Wrapper Development

This directory contains the XC8 Wrapper package development environment.

## Quick Start

```bash
# Install in development mode
pip install -e .

# Install with development dependencies  
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=xc8_wrapper

# Format code
black .

# Type checking
mypy .

# Build package
python -m build
```

## Package Structure

```
xc8_wrapper/
├── pyproject.toml          # Modern Python package configuration
├── README.md              # Package documentation
├── LICENSE                # MIT license
├── .gitignore            # Git ignore rules
├── xc8_wrapper/          # Main package directory
│   ├── __init__.py       # Package initialization
│   ├── cli.py           # Command-line interface
│   └── core.py          # Core functionality
└── tests/               # Test suite
    ├── __init__.py
    ├── test_cli.py
    └── test_core.py
```

## Usage

After installation, you can use the wrapper as:

```bash
# Command-line tool
xc8-wrapper --cpu PIC16F876A --xc8-version 3.00

# Python module
python -m xc8_wrapper.cli --cpu PIC16F876A --xc8-version 3.00

# Python API
from xc8_wrapper import get_xc8_tool_path, handle_cc_tool
```
