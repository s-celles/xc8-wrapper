# Frequently Asked Questions

Common questions and solutions for XC8 Wrapper.

## Installation Questions

### Q: How do I install XC8 Wrapper?

**A:** Install using pip:
```bash
pip install xc8-wrapper
```

For development:
```bash
git clone https://github.com/s-celles/xc8-wrapper.git
cd xc8-wrapper
pip install -e .[dev]
```

### Q: Do I need to install the XC8 compiler separately?

**A:** Yes! XC8 Wrapper is a wrapper tool that requires the actual Microchip XC8 compiler to be installed on your system. Download it from [Microchip's website](https://www.microchip.com/en-us/tools-resources/develop/mplab-xc-compilers).

### Q: Which Python versions are supported?

**A:** Python 3.9 and above. We test on Python 3.9, 3.10, 3.11, and 3.12.

## Usage Questions

### Q: How do I specify which XC8 version to use?

**A:** Use the `--xc8-version` flag:
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c
```

Or specify the exact path:
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-path "/path/to/xc8-cc" main.c
```

### Q: What microcontrollers are supported?

**A:** Any microcontroller supported by the XC8 compiler. Common examples:
- **PIC16 series**: PIC16F877A, PIC16F876A, PIC16F84A
- **PIC18 series**: PIC18F4550, PIC18F2550, PIC18F4520
- **PIC12 series**: PIC12F675, PIC12F629

### Q: How do I compile multiple source files?

**A:** Currently, XC8 Wrapper supports single-file compilation. For multi-file projects, consider:
1. Using include files
2. Creating a single main.c that includes other .c files
3. Using XC8 directly for complex multi-file projects

Multi-file support is planned for future versions.

### Q: Can I use custom compiler flags?

**A:** Yes! Use `--compile-flag` and `--link-flag`:
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
    --compile-flag "-Wall" \
    --link-flag "-Wl,--gc-sections"
```

## Assembly Questions

### Q: Does XC8 Wrapper support assembly programming?

**A:** Yes! Use the `as` command for PIC assembly:
```bash
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 main.s
```

### Q: What assembly formats are supported?

**A:** XC8 Wrapper supports PIC assembly using the pic-as assembler that comes with XC8. It supports:
- PIC14 family (PIC16F series)
- PIC16 family (PIC18F series) 
- Intel HEX output format
- Motorola S-record format
- Binary format

### Q: How do I generate listing files in assembly?

**A:** Use the `--passthrough` option to pass pic-as specific flags:
```bash
xc8-wrapper as --cpu PIC16F877A --passthrough="-list -map" main.s
```

### Q: How do I debug assembly code?

**A:** Enable debug information generation:
```bash
xc8-wrapper as --cpu PIC16F877A --passthrough="-g -gdwarf-3 -list" main.s
```

### Q: Can I mix C and assembly files?

**A:** Currently, XC8 Wrapper handles C and assembly separately. For mixed projects:
1. Assemble your `.s` files with `xc8-wrapper as`
2. Compile your `.c` files with `xc8-wrapper cc`
3. Use XC8 directly for linking mixed object files

Mixed-language project support is planned for future versions.

### Q: What's the difference between using `cc` and `as` commands?

**A:** 
- `cc` command: Compiles C source files using `xc8-cc`
- `as` command: Assembles assembly source files using `pic-as`

Both are part of the XC8 toolchain but serve different purposes.

### Q: How do I specify output format for assembly?

**A:** Use passthrough options:
```bash
# Intel HEX format (default)
xc8-wrapper as --cpu PIC16F877A --passthrough="-inhx32" main.s

# Motorola S-record format
xc8-wrapper as --cpu PIC16F877A --passthrough="-motorola" main.s

# Binary format
xc8-wrapper as --cpu PIC16F877A --passthrough="-binary" main.s
```

## Platform-Specific Questions

### Q: XC8 Wrapper can't find my XC8 installation on Windows

**A:** XC8 Wrapper checks these locations automatically:
- `C:\Program Files\Microchip\xc8\`
- `C:\Program Files (x86)\Microchip\xc8\`

If installed elsewhere, use `--xc8-path`:
```bash
xc8-wrapper cc --cpu PIC16F877A \
    --xc8-path "C:\CustomPath\xc8\v3.00\bin\xc8-cc.exe"
```

### Q: XC8 Wrapper can't find my XC8 installation on Linux/macOS

**A:** Standard locations checked:
- `/opt/microchip/bin/`
- `/usr/local/microchip/bin/`
- `/opt/microchip/xc8/v{version}/bin/` (versioned alternative)
- `/usr/local/microchip/xc8/v{version}/bin/` (versioned alternative)
- `/Applications/microchip/xc8/` (macOS)

For custom installations:
```bash
xc8-wrapper cc --cpu PIC16F877A \
    --xc8-path "/custom/path/xc8/v3.00/bin/xc8-cc"
```

### Q: Why do I get "Permission denied" errors on Linux/macOS?

**A:** Make sure the XC8 executable has execute permissions:
```bash
chmod +x /path/to/xc8/bin/xc8-cc
```

## Error Messages

### Q: "Unsupported XC8 tool: xyz"

**A:** Currently only the `cc` and `as` tools are supported. Use:
```bash
# For C compilation
xc8-wrapper cc --cpu PIC16F877A main.c

# For assembly
xc8-wrapper as --cpu PIC16F877A main.s
```

### Q: "CPU is required for cc tool" or "CPU is required for as tool"

**A:** Always specify the target microcontroller:
```bash
# For C
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c

# For assembly
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 main.s
```

### Q: "PIC-AS executable not found"

**A:** This means pic-as isn't found. Solutions:
1. Ensure XC8 is properly installed (pic-as comes with XC8)
2. Use `--xc8-path` to specify the path to pic-as
3. Check that pic-as has execute permissions (Linux/macOS)

```bash
# Specify pic-as path explicitly
xc8-wrapper as --cpu PIC16F877A \
    --xc8-path "/path/to/pic-as" main.s
```

### Q: "Source file not found: src/main.c"

**A:** Ensure your source file exists. Default location is `src/main.c`. To use a different structure:
```bash
# Custom source directory and file
xc8-wrapper cc --cpu PIC16F877A \
    --source-dir my_src \
    --main-c-file my_main.c
```

### Q: "XC8 executable not found"

**A:** This means XC8 isn't installed or not in the expected location. Solutions:
1. Install XC8 from Microchip
2. Use `--xc8-path` to specify the exact location
3. Add XC8 to your PATH environment variable

### Q: Compilation succeeds but no output files

**A:** Check the build directory (default: `build/`). Use `-v` for detailed output:
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 -v
```

## Performance Questions

### Q: Compilation is slow. How can I speed it up?

**A:** Try these optimization strategies:
1. Use `-O0` for debug builds (fastest compilation)
2. Use `--save-temps` only when debugging
3. Ensure your antivirus isn't scanning the build directory
4. Use SSD storage for better I/O performance

### Q: What optimization level should I use?

**A:** Recommended levels:
- **Development**: `-O0` or `-Og` (fast compilation, debuggable)
- **Testing**: `-O1` or `-O2` (good balance)
- **Production**: `-O2` (recommended) or `-Os` (size-critical)
- **Performance-critical**: `-O3` (aggressive optimization)

## Development Questions

### Q: How do I contribute to XC8 Wrapper?

**A:** See our [Development Guide](development.md):
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Q: How do I report bugs?

**A:** Use our [GitHub Issues](https://github.com/s-celles/xc8-wrapper/issues):
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include system information (OS, Python version, XC8 version)
4. Attach relevant files if possible

### Q: Can I use XC8 Wrapper in my commercial project?

**A:** Yes! XC8 Wrapper is released under the MIT License, which allows commercial use. However, remember that the XC8 compiler itself has its own licensing terms from Microchip.

## Integration Questions

### Q: How do I integrate XC8 Wrapper with my build system?

**A:** XC8 Wrapper works with any build system:

**Makefile:**
```makefile
build:
	xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c
```

**CMake:**
```cmake
add_custom_target(firmware
    COMMAND xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c
)
```

**GitHub Actions:**
```yaml
- name: Build firmware
  run: xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c
```

### Q: Can I use XC8 Wrapper with Docker?

**A:** Yes, but you'll need to install XC8 in your Docker container:
```dockerfile
FROM python:3.9

# Install XC8 Wrapper
RUN pip install xc8-wrapper

# Install XC8 compiler (implementation depends on your needs)
# COPY xc8-installer.run /tmp/
# RUN chmod +x /tmp/xc8-installer.run && /tmp/xc8-installer.run

# Your application code
COPY . /app
WORKDIR /app
```

## Licensing Questions

### Q: What's the license for XC8 Wrapper?

**A:** XC8 Wrapper is licensed under the MIT License, which is very permissive and allows both personal and commercial use.

### Q: What about the XC8 compiler license?

**A:** The XC8 compiler is proprietary software from Microchip. You need to:
1. Download it from Microchip's website
2. Accept their license terms
3. Comply with their licensing requirements

XC8 Wrapper doesn't include or redistribute any Microchip software.

### Q: Can I redistribute XC8 Wrapper?

**A:** Yes, under the terms of the MIT License. You can include it in your projects, modify it, and redistribute it.

## Still Have Questions?

- 📚 Check the [Getting Started](getting-started.md) guide
- 📖 Read the [CLI Reference](cli-reference.md)
- 🔍 Browse [Examples](examples.md)
- 🐛 Report issues on [GitHub](https://github.com/s-celles/xc8-wrapper/issues)
- 💬 Start a [discussion](https://github.com/s-celles/xc8-wrapper/discussions)
