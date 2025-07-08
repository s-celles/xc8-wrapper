# 🔧 XC8 Wrapper

<div align="center">

[![CI](https://github.com/s-celles/xc8-wrapper/actions/workflows/ci.yml/badge.svg)](https://github.com/s-celles/xc8-wrapper/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/s-celles/xc8-wrapper/branch/main/graph/badge.svg)](https://codecov.io/gh/s-celles/xc8-wrapper)
[![PyPI version](https://badge.fury.io/py/xc8-wrapper.svg)](https://badge.fury.io/py/xc8-wrapper)
[![Python versions](https://img.shields.io/pypi/pyversions/xc8-wrapper.svg)](https://pypi.org/project/xc8-wrapper/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Modern, secure, and cross-platform wrapper for the Microchip XC8 compiler**

</div>

---

## 🚀 Quick Start

```bash
# Install
pip install xc8-wrapper

# Compile a PIC project (CC tool)
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00

# Create library archive (AR tool)
xc8-wrapper ar r mylib.a file1.p1 file2.p1 --xc8-version 3.00
```

## ✨ Features

- **🎯 Hierarchical CLI** with tool-specific arguments (cc, ar)
- **🔒 Security-first** design with input validation and safe execution
- **🌍 Cross-platform** support for Windows, Linux, and macOS
- **⚡ Smart XC8 detection** - automatically finds your compiler installation
- **🧪 Well tested** with comprehensive test suite (88%+ coverage)

## 🛠️ Supported Tools

- **`cc`**: C compiler, assembler, and linker (xc8-cc)
- **`ar`**: Archiver/librarian for creating static libraries (xc8-ar)

## 📝 Basic Usage

### Compiler (CC Tool)
```bash
# Basic compilation
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00

# With optimization and defines
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 -O2 -DDEBUG=1

# Custom paths and flags
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
  --source-dir src --build-dir build \
  --compile-flag "-Wall" --link-flag "-Wl,--gc-sections"
```

### Archiver (AR Tool)
```bash
# Create library
xc8-wrapper ar r mylib.a file1.p1 file2.p1 --xc8-version 3.00

# Add files with verbose output
xc8-wrapper ar rv mylib.a *.p1 --xc8-version 3.00

# List archive contents
xc8-wrapper ar t mylib.a --xc8-version 3.00

# Extract files from archive
xc8-wrapper ar x mylib.a --xc8-version 3.00
```

## 📚 Documentation

**Complete documentation is available at:**
**🌐 [https://s-celles.github.io/xc8-wrapper/](https://s-celles.github.io/xc8-wrapper/)**

### Quick Links
- [📦 Installation Guide](https://s-celles.github.io/xc8-wrapper/installation/)
- [🚀 Getting Started Tutorial](https://s-celles.github.io/xc8-wrapper/getting-started/)
- [📖 CLI Reference](https://s-celles.github.io/xc8-wrapper/cli-reference/)

## 📋 Requirements

- **Python**: 3.9+
- **XC8 Compiler**: 2.xx, 3.xx, ... (must be installed separately)
- **OS**: Windows, macOS, or Linux

## ⚖️ License

**Wrapper Code**: MIT License (see [LICENSE](LICENSE) file)
**XC8 Compiler**: Proprietary Microchip license - [download from Microchip](https://www.microchip.com/en-us/tools-resources/develop/mplab-xc-compilers)

## 🤝 Contributing

Contributions welcome! See the [Development Guide](https://s-celles.github.io/xc8-wrapper/) for setup instructions and contribution guidelines.

---

<div align="center">

Made with ❤️ by [Sébastien Celles](https://github.com/s-celles)

</div>
