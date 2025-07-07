# XC8 Wrapper

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

# Format code
black .

# Type checking
mypy .
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
