# Installation Guide

This guide covers all the ways to install and set up XC8 Wrapper on your system.

## Requirements

Before installing XC8 Wrapper, ensure you have:

- **Python 3.9 or higher** installed on your system
- **Microchip XC8 Compiler** installed (is have been tested with xc8-v3.00)
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+, CentOS 7+)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

This is the easiest way to install XC8 Wrapper:

```bash
pip install xc8-wrapper
```

### Method 2: Install from Source

For the latest development version or to contribute:

```bash
# Clone the repository
git clone https://github.com/s-celles/xc8-wrapper.git
cd xc8-wrapper

# Install in development mode
pip install -e .
```

### Method 3: Install Specific Version

To install a specific version:

```bash
pip install xc8-wrapper==0.1.0
```

## Platform-Specific Instructions

### Windows

1. **Install Python** (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/)
   - Or use Anaconda/Miniconda

2. **Install XC8 Wrapper**:
   ```cmd
   pip install xc8-wrapper
   ```

3. **Verify Installation**:
   ```cmd
   xc8-wrapper --version
   ```

### macOS

1. **Install Python** (if not already installed):
   ```bash
   # Using Homebrew
   brew install python

   # Or download from python.org
   ```

2. **Install XC8 Wrapper**:
   ```bash
   pip install xc8-wrapper
   ```

3. **Verify Installation**:
   ```bash
   xc8-wrapper --version
   ```

### Linux (Ubuntu/Debian)

1. **Install Python and pip**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Install XC8 Wrapper**:
   ```bash
   pip3 install xc8-wrapper
   ```

3. **Verify Installation**:
   ```bash
   xc8-wrapper --version
   ```

### Linux (CentOS/RHEL/Fedora)

1. **Install Python and pip**:
   ```bash
   # CentOS/RHEL
   sudo yum install python3 python3-pip

   # Fedora
   sudo dnf install python3 python3-pip
   ```

2. **Install XC8 Wrapper**:
   ```bash
   pip3 install xc8-wrapper
   ```

3. **Verify Installation**:
   ```bash
   xc8-wrapper --version
   ```

## XC8 Compiler Installation

XC8 Wrapper requires the Microchip XC8 compiler to be installed. Here's where to get it:

### Download XC8 Compiler

1. Visit [Microchip's official page](https://www.microchip.com/en-us/development-tools-tools-and-software/mplab-xc-compilers/xc8)
2. Download the appropriate version for your operating system
3. Install following Microchip's instructions

### Expected Installation Locations

XC8 Wrapper automatically detects XC8 installations in these standard locations:

#### Windows
- `C:\Program Files\Microchip\xc8\v{version}\bin\`
- `C:\Program Files (x86)\Microchip\xc8\v{version}\bin\`

#### macOS
- `/Applications/microchip/xc8/v{version}/bin/`
- `/opt/microchip/xc8/v{version}/bin/`

#### Linux
- `/opt/microchip/xc8/v{version}/bin/`
- `/usr/local/microchip/xc8/v{version}/bin/`

## Virtual Environment Setup (Recommended)

For isolated Python environments:

```bash
# Create virtual environment
python -m venv xc8-env

# Activate it
# Windows:
xc8-env\Scripts\activate
# macOS/Linux:
source xc8-env/bin/activate

# Install XC8 Wrapper
pip install xc8-wrapper
```

## Troubleshooting

### Common Issues

#### "xc8-wrapper: command not found"

**Problem**: The command is not in your PATH.

**Solutions**:
1. **Check installation**:
   ```bash
   pip show xc8-wrapper
   ```

2. **Find installation location**:
   ```bash
   python -m xc8_wrapper.cli --version
   ```

3. **Add to PATH** (if needed):
   - Find where pip installs scripts (usually `~/.local/bin` on Linux/macOS)
   - Add that directory to your PATH

#### "XC8 not found" Error

**Problem**: XC8 Wrapper can't find your XC8 installation.

**Solutions**:
1. **Verify XC8 installation**:
   - Check if XC8 is installed in standard locations
   - Try running `xc8-cc --version` directly

2. **Use custom path**:
   ```bash
   xc8-wrapper --xc8-path "/path/to/xc8-cc" --cpu PIC16F877A
   ```

3. **Check version format**:
   ```bash
   # Correct format
   xc8-wrapper --xc8-version 3.00 --cpu PIC16F877A
   ```

#### Permission Errors

**Problem**: Permission denied during installation.

**Solutions**:
1. **Use user installation**:
   ```bash
   pip install --user xc8-wrapper
   ```

2. **Use virtual environment** (recommended):
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # or myenv\Scripts\activate on Windows
   pip install xc8-wrapper
   ```

### Getting Help

If you encounter issues:

1. **Check the FAQ**: [FAQ page](faq.md)
2. **Search existing issues**: [GitHub Issues](https://github.com/s-celles/xc8-wrapper/issues)
3. **Create a new issue**: Include your OS, Python version, and error messages
4. **Ask in discussions**: [GitHub Discussions](https://github.com/s-celles/xc8-wrapper/discussions)

## Next Steps

Once installed, check out:
- [Getting Started Guide](getting-started.md) - Create your first project
- [CLI Reference](cli-reference.md) - Learn all available commands
- [Examples](examples.md) - See real-world usage examples
