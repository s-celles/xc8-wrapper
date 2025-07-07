# CLI Reference

Complete reference for the XC8 Wrapper command-line interface.

## Basic Syntax

```bash
xc8-wrapper [OPTIONS]
```

## Global Options

### Help and Version
- `--help`, `-h`: Show help message and exit
- `--version`: Show program version and exit

### Tool Selection
- `--tool {cc}`: XC8 tool to use (currently only 'cc' is supported)

### XC8 Compiler Location
- `--xc8-version VERSION`: XC8 toolchain version (e.g., '3.00', '2.40')
- `--xc8-path PATH`: Full path to XC8 tool executable (overrides version)

### Target Configuration
- `--cpu CPU`: Target microcontroller (**required** for cc tool)

## Preprocessor Options

### Definitions
- `-D SYMBOL`, `--define SYMBOL`: Define preprocessor symbol
- `-U SYMBOL`, `--undefine SYMBOL`: Undefine preprocessor symbol

**Examples:**
```bash
# Define single symbols
xc8-wrapper --cpu PIC16F877A -D DEBUG

# Define with values
xc8-wrapper --cpu PIC16F877A -D _XTAL_FREQ=20000000 -D LED_PIN=0

# Multiple definitions
xc8-wrapper --cpu PIC16F877A -D DEBUG=1 -D VERSION=2 -D BOARD_REV=3
```

### Include Paths
- `-I PATH`, `--include PATH`: Add include directory

**Examples:**
```bash
# Single include path
xc8-wrapper --cpu PIC16F877A -I ./headers

# Multiple include paths
xc8-wrapper --cpu PIC16F877A -I ./include -I ./lib -I ../common
```

### Preprocessor Control
- `-C`, `--keep-comments`: Keep comments in preprocessed output
- `-E`, `--preprocess-only`: Preprocess only, don't compile
- `-H`, `--list-headers`: List included header files
- `-dM`, `--list-macros`: List all defined macros

## Compilation Options

### Compilation Modes
- `-c`, `--compile-only`: Compile to object file only (no linking)
- `-S`, `--assembly-only`: Compile to assembly file only

### Output Control
- `-v`, `--verbose`: Enable verbose output
- `-w`, `--suppress-warnings`: Suppress all warning messages
- `--save-temps`: Don't delete intermediate files

## Optimization Options

### Optimization Levels
- `-O0`: No optimization (fastest compilation)
- `-O1`: Basic optimization
- `-O2`: Standard optimization (recommended)
- `-O3`: Aggressive optimization
- `-Og`: Debug-friendly optimization
- `-Os`: Size optimization

**Examples:**
```bash
# No optimization (debugging)
xc8-wrapper --cpu PIC16F877A -O0

# Size optimization (resource-constrained projects)
xc8-wrapper --cpu PIC16F877A -Os

# Speed optimization (performance-critical code)
xc8-wrapper --cpu PIC16F877A -O2
```

## Language Standards

### C Standard Selection
- `--std STANDARD`: Specify C language standard

**Supported standards:**
- `c89`, `c90`: ANSI C (1989/1990)
- `c99`: ISO C99
- `c11`: ISO C11

**Examples:**
```bash
# Use C99 standard
xc8-wrapper --cpu PIC16F877A --std c99

# Use C11 standard (default)
xc8-wrapper --cpu PIC16F877A --std c11
```

## Custom Flags

### Advanced Flag Passing
- `--compile-flag FLAG`: Add custom compilation flag
- `--link-flag FLAG`: Add custom linking flag

**Examples:**
```bash
# Custom compile flags
xc8-wrapper --cpu PIC16F877A --compile-flag "-fdata-sections" --compile-flag "-ffunction-sections"

# Custom link flags
xc8-wrapper --cpu PIC16F877A --link-flag "-Wl,--gc-sections"

# Mixed custom flags
xc8-wrapper --cpu PIC16F877A \
    --compile-flag "-Wall" \
    --link-flag "-Wl,-Map=custom.map" \
    --compile-flag "-Wextra"
```

## File and Directory Options

### Input/Output Configuration
- `--source-dir DIR`: Source directory (default: 'src')
- `--build-dir DIR`: Build directory (default: 'build')
- `--main-c-file FILE`: Main C source file (default: 'main.c')

### Output Files
- `--output-hex FILE`: Output HEX file name (default: 'main.hex')
- `--output-elf FILE`: Output ELF file name (default: 'main.elf')
- `--output-p1 FILE`: Output object file name (default: 'main.p1')
- `--output-map FILE`: Output MAP file name (default: 'main.map')
- `--memory-file FILE`: Memory summary file (default: 'memoryfile.xml')

**Examples:**
```bash
# Custom project structure
xc8-wrapper --cpu PIC16F877A \
    --source-dir firmware \
    --build-dir output \
    --main-c-file blink.c

# Custom output files
xc8-wrapper --cpu PIC16F877A \
    --output-hex led_blink.hex \
    --output-elf led_blink.elf
```

## Common Command Patterns

### Development Workflow

**Quick compile (development):**
```bash
xc8-wrapper --cpu PIC16F877A --xc8-version 3.00 -O0 --verbose
```

**Production build:**
```bash
xc8-wrapper --cpu PIC16F877A --xc8-version 3.00 -Os --std c99
```

**Debug build:**
```bash
xc8-wrapper --cpu PIC16F877A --xc8-version 3.00 -Og -D DEBUG=1 --save-temps
```

### Project-Specific Examples

**Library project:**
```bash
xc8-wrapper --cpu PIC16F877A --xc8-version 3.00 \
    --compile-only \
    -I ./include \
    -D LIBRARY_VERSION=1.0
```

**Multi-file project:**
```bash
# Note: Currently only single-file compilation is supported
# Multi-file support planned for future versions
```

### Testing and Validation

**Preprocessor output:**
```bash
xc8-wrapper --cpu PIC16F877A --xc8-version 3.00 \
    --preprocess-only \
    --keep-comments \
    --list-headers
```

**Assembly generation:**
```bash
xc8-wrapper --cpu PIC16F877A --xc8-version 3.00 \
    --assembly-only \
    --verbose
```

## Platform-Specific Notes

### Windows
- Use forward slashes or double backslashes in paths
- XC8 executable names include `.exe` extension automatically

### macOS/Linux
- Use standard Unix path conventions
- XC8 executable names automatically drop `.exe` extension

## Error Handling

### Common Error Messages

**"Unsupported XC8 tool"**
- Only 'cc' tool is currently supported
- Solution: Use `--tool cc`

**"XC8 not found"**
- XC8 compiler not detected in standard locations
- Solutions: Install XC8 or use `--xc8-path`

**"CPU is required"**
- Target microcontroller not specified
- Solution: Add `--cpu MICROCONTROLLER`

**"Invalid version format"**
- Version string contains invalid characters
- Solution: Use format like `3.00`, `2.40`

**"Source file not found"**
- Source file doesn't exist in specified location
- Solutions: Check file path, use `--source-dir` and `--main-c-file`

### Debugging Tips

1. **Use verbose output**: Add `--verbose` to see detailed execution
2. **Check file paths**: Verify source and build directories exist
3. **Validate XC8**: Test XC8 directly with `xc8-cc --version`
4. **Save intermediates**: Use `--save-temps` to inspect generated files

## Advanced Usage

### Custom XC8 Installation
```bash
# Using custom XC8 path
xc8-wrapper --xc8-path "/custom/path/to/xc8-cc" --cpu PIC16F877A

# Multiple XC8 versions
xc8-wrapper --xc8-version 2.40 --cpu PIC16F877A  # Legacy project
xc8-wrapper --xc8-version 3.00 --cpu PIC16F877A  # Current project
```

### Integration with Build Systems

**Makefile integration:**
```makefile
CHIP = PIC16F877A
XC8_VERSION = 3.00

build:
	xc8-wrapper --cpu $(CHIP) --xc8-version $(XC8_VERSION) -O2

debug:
	xc8-wrapper --cpu $(CHIP) --xc8-version $(XC8_VERSION) -Og -D DEBUG=1
```

**Shell script integration:**
```bash
#!/bin/bash
set -e

CHIP="${1:-PIC16F877A}"
VERSION="${2:-3.00}"

echo "Building for $CHIP with XC8 $VERSION..."
xc8-wrapper --cpu "$CHIP" --xc8-version "$VERSION" -O2 --verbose
echo "Build complete!"
```

## Related Documentation

- [Getting Started](getting-started.md) - Basic usage examples
- [Examples](examples.md) - Real-world usage scenarios
- [Configuration](configuration.md) - Advanced configuration options
- [FAQ](faq.md) - Frequently asked questions
