# XC8 Wrapper Documentation

A modern, secure, and cross-platform wrapper for the Microchip XC8 compiler toolchain.

[Get started now](#getting-started){ .md-button .md-button--primary }
[View it on GitHub](https://github.com/s-celles/xc8-wrapper){ .md-button }

---

!!! warning
    This project is currently in active development. APIs may change between versions.

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

# Compile with optimization
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -O2 --verbose
```

## Getting Started

1. **[Install XC8 Wrapper](installation.md)** - Complete installation guide
2. **[Create your first project](getting-started.md)** - Step-by-step tutorial
3. **[Learn the CLI](cli-reference.md)** - Complete command reference
4. **[See examples](examples.md)** - Real-world usage patterns

## Features

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

## Contributing

We welcome contributions! Please see our [Development Guide](development.md) for information on how to contribute to this project.

---

## About

This project is maintained by [Sébastien Celles](https://github.com/s-celles) and is licensed under the [MIT License](https://github.com/s-celles/xc8-wrapper/blob/main/LICENSE).
