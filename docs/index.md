# XC8 Wrapper Documentation

A modern, secure, and cross-platform wrapper for the Microchip XC8 compiler toolchain.

[![CI](https://github.com/s-celles/xc8-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/s-celles/xc8-wrapper/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/s-celles/xc8-wrapper/branch/main/graph/badge.svg)](https://codecov.io/gh/s-celles/xc8-wrapper)
[![PyPI version](https://badge.fury.io/py/xc8-wrapper.svg)](https://badge.fury.io/py/xc8-wrapper)
[![Python versions](https://img.shields.io/pypi/pyversions/xc8-wrapper.svg)](https://pypi.org/project/xc8-wrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is XC8 Wrapper?

XC8 Wrapper is a Python-based command-line tool that provides a modern, user-friendly interface to the Microchip XC8 compiler. It simplifies PIC microcontroller development by offering:

- **🚀 Easy-to-use CLI** with intuitive commands and options
- **🔒 Security-first design** with input validation and safe execution
- **🌍 Cross-platform support** for Windows, Linux, and macOS
- **🎨 Rich terminal output** with colors and progress indicators
- **⚡ Smart XC8 detection** that finds your compiler installation automatically
- **🧪 Comprehensive testing** with 78%+ code coverage

## Quick Start

### Installation

```bash
pip install xc8-wrapper
```

### Basic Usage

```bash
# Compile a simple PIC project
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A

# Compile with custom source directory
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A --source-dir my_project --main-c-file main.c

# Use optimization and verbose output
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -O2 --verbose
```

## Navigation

- [📋 **Installation Guide**](installation.md) - Complete installation instructions
- [🚀 **Getting Started**](getting-started.md) - Your first project with XC8 Wrapper
- [📚 **CLI Reference**](cli-reference.md) - Complete command-line interface documentation
- [🔧 **Configuration**](configuration.md) - Advanced configuration and customization
- [💻 **Development**](development.md) - Contributing and development setup
- [❓ **FAQ**](faq.md) - Frequently asked questions
- [📖 **Examples**](examples.md) - Real-world usage examples
- [🔗 **API Reference**](api-reference.md) - Python API documentation

## Features Overview

### Cross-Platform Compatibility
- **Windows**: Supports both 64-bit and 32-bit Program Files locations
- **macOS**: Checks `/Applications` and `/opt` installation paths
- **Linux**: Supports `/opt` and `/usr/local` installation directories

### Security Features
- Input validation and sanitization
- Path traversal protection
- Executable whitelist enforcement
- Secure subprocess execution

### Developer Experience
- Colorized terminal output
- Progress indicators and status messages
- Detailed error reporting with helpful suggestions
- Comprehensive logging and debugging options

## Requirements

- **Python**: 3.9 or higher
- **XC8 Compiler**: Any version (2.xx, 3.xx, 4.xx)
- **Operating System**: Windows, macOS, or Linux

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/s-celles/xc8-wrapper/blob/main/LICENSE) file for details.

## Contributing

We welcome contributions! Please see our [Development Guide](development.md) for information on how to contribute to this project.

## Support

- 📖 **Documentation**: You're reading it!
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/s-celles/xc8-wrapper/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/s-celles/xc8-wrapper/discussions)
- 📧 **Contact**: [s.celles@gmail.com](mailto:s.celles@gmail.com)
