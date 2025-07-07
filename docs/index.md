# XC8 Wrapper Documentation

A modern, 1. **[📦1. **[📦1.3. **[| [📦 Installation](installation.md) | Installing XC8 Wrapper and XC8 compiler |
| [🚀 Getting Started](getting-started.md) | Your first PIC project tutorial |
| [�📖 CLI Reference](cli-reference.md) | Complete command-line documentation |
| [💡 Examples](examples.md) | Real-world usage examples and patterns |
| [❓ FAQ](faq.md) | Frequently asked questions and solutions |
| [🛠️ Development](development.md) | Contributing and development guide |n the CLI](cli-reference.md)** - Complete command reference**[📦 Install XC8 Wrapper](installation.md)** - Complete installation guideIns| [📦 | [🚀 Getting Started](getting-started.md) | Your first PIC project tutorial |nstallation](installation/) | Installing XC8 Wrapper and XC8 compiler |
| [🚀 Getting Started](getting-started/) | Your first PIC project tutorial |
| [📖 CLI Reference](cli-reference/) | Complete command-line documentation |
| [💡 Examples](examples/) | Real-world usage examples and patterns |
| [❓ FAQ](faq/) | Frequently asked questions and solutions |
| [🛠️ Development](development/) | Contributing and development guide |C8 Wrapper](installation/)** - Complete installation guide
2. **[🚀 Create your first project](getting-started/)** - Step-by-step tutorial with LED blink example
3. **[📖 Learn the CLI](cli-reference/)** - Complete command reference
4. **[💡 See examples](examples/)** - Real-world usage patterns and integrations| [📦 Installation](installation.md) | Installing XC8 Wrapper and XC8 compiler |
| [🚀 Getting Started](getting-started.md) | Your first PIC project tutorial |
| [📖 CLI Reference](cli-reference.md) | Complete command-line documentation |
| [💡 Examples](examples.md) | Real-world usage examples and patterns |
| [❓ FAQ](faq.md) | Frequently asked questions and solutions |
| [🛠️ Development](development.md) | Contributing and development guide |C8 Wrapper](installation/)** - Complete installation guide
2. **[🚀 Create your first project](getting-started/)** - Step-by-step tutorial with LED blink example
3. **[📖 Learn the CLI](cli-reference/)** - Complete command reference
4. **[💡 See examples](examples/)** - Real-world usage patterns and integrationsre, and cross-platform wrapper for the Microchip XC8 compiler toolchain.

[Get started now](#getting-started){ .md-button .md-button--primary }
[View it on GitHub](https://github.com/s-celles/xc8-wrapper){ .md-button }

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

# Compile with optimization and verbose output
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -O2 --verbose
```

## Getting Started

1. **[� Install XC8 Wrapper](installation.html)** - Complete installation guide
2. **[🚀 Create your first project](getting-started.md)** - Step-by-step tutorial with LED blink example
3. **[� Learn the CLI](cli-reference.html)** - Complete command reference
4. **[💡 See examples](examples.md)** - Real-world usage patterns and integrations

## Documentation

| Section | Description |
|---------|-------------|
| [� Installation](installation.html) | Installing XC8 Wrapper and XC8 compiler |
| [� Getting Started](getting-started.html) | Your first PIC project tutorial |
| [📖 CLI Reference](cli-reference.html) | Complete command-line documentation |
| [� Examples](examples.html) | Real-world usage examples and patterns |
| [❓ FAQ](faq.html) | Frequently asked questions and solutions |
| [🛠️ Development](development.html) | Contributing and development guide |

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
