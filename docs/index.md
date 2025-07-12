# 🔧 XC8 Wrapper Documentation

A modern, secure, and cross-platform wrapper for the Microchip XC8 compiler toolchain.

[Get started now](#getting-started){ .md-button .md-button--primary }
[View it on GitHub](https://github.com/s-celles/xc8-wrapper){ .md-button }

!!! warning
    This project is currently in active development. APIs may change between versions.

!!! info "AI-Generated Content Notice"
A significant portion of this project's content (including code, documentation, and examples) has been generated using AI assistance. Please review all code and documentation carefully before use in production environments. We recommend thorough testing and validation of any AI-generated components.

## 🌟 What is XC8 Wrapper?

XC8 Wrapper is a Python-based command-line tool that provides a modern, user-friendly interface to the Microchip XC8 compiler. It simplifies PIC microcontroller development by offering:

- **🚀 Easy-to-use CLI** with intuitive commands and options
- **🔒 Security-first design** with input validation and safe execution
- **🌍 Cross-platform support** for Windows, Linux, and macOS
- **🎨 Rich terminal output** with colors and progress indicators
- **⚡ Smart XC8 detection** that finds your compiler installation automatically
- **🧪 Comprehensive testing** with 78%+ code coverage

## 🚀 Quick Start

### 📦 Installation

```bash
pip install xc8-wrapper
```

### 💻 Basic Usage

```bash
# Compile a simple PIC project
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A

# Compile with optimization and verbose output
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -O2 --verbose
```

## Getting Started

1. **[📦 Install XC8 Wrapper](installation.md)** - Complete installation guide
2. **[🚀 Create your first project](getting-started.md)** - Step-by-step tutorial with LED blink example
3. **[📖 Learn the CLI](cli-reference.md)** - Complete command reference
4. **[💡 See examples](examples.md)** - Real-world usage patterns and integrations

## Documentation

| Section | Description |
|---------|-------------|
| [📦 Installation](installation.md) | Installing XC8 Wrapper and XC8 compiler |
| [🚀 Getting Started](getting-started.md) | Your first PIC project tutorial |
| [📖 CLI Reference](cli-reference.md) | Complete command-line documentation |
| [💡 Examples](examples.md) | Real-world usage examples and patterns |
| [❓ FAQ](faq.md) | Frequently asked questions and solutions |
| [🛠️ Development](development.md) | Development setup and tools guide |
| [🤝 Contributing](contributing.md) | Contributing guidelines and workflow |

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
- **XC8 Compiler**: Any version (2.xx, 3.xx, ...)
- **Operating System**: Windows, macOS, or Linux

## Related Projects

### 🔧 IPECMD Wrapper
Complete your PIC development workflow with our companion project:

- **📦 Repository**: [s-celles/ipecmd-wrapper](https://github.com/s-celles/ipecmd-wrapper)
- **📚 Documentation**: [s-celles.github.io/ipecmd-wrapper](https://s-celles.github.io/ipecmd-wrapper/)
- **🎯 Purpose**: Modern Python wrapper for MPLAB IPE command-line programming tool

**Perfect Combination**: Use XC8 Wrapper to compile your PIC code, then use IPECMD Wrapper to program it to your microcontroller!

```bash
# Complete workflow example
pip install xc8-wrapper ipecmd-wrapper

# 1. Compile with XC8 Wrapper
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A

# 2. Program with IPECMD Wrapper
ipecmd-wrapper -P 16F877A -T PK3 -F dist/main.hex -W 5.0
```

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/s-celles/xc8-wrapper/blob/main/LICENSE) file for details.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](contributing.md) for detailed information on how to contribute to this project.

## 💬 Support

- 📖 **Documentation**: You're reading it!
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/s-celles/xc8-wrapper/issues)
- 💡 **Feature Requests**: [GitHub Discussions](https://github.com/s-celles/xc8-wrapper/discussions)
- 📧 **Contact**: [s-celles](https://linktr.ee/SebastienCelles)
