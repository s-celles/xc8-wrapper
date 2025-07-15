# CLI Reference

Complete reference for the XC8 Wrapper command-line interface.

## Basic Syntax

```bash
xc8-wrapper [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS] [FILES...]
```

### Available Commands
- `install`: Install XC8 compiler
- `cc`: C compiler, assembler, and linker (equivalent to xc8-cc)
- `ar`: Archive/librarian tool (not yet implemented)

### Global Options
- `--help`, `-h`: Show help message and exit
- `--version`: Show program version and exit

## CC Command (C Compiler)

### Basic Usage
```bash
xc8-wrapper cc [OPTIONS] [FILES...]
```

### XC8 Compiler Location
- `--xc8-version VERSION`: XC8 toolchain version (e.g., '3.00', '2.40')
- `--xc8-path PATH`: Full path to XC8 tool executable (overrides version)

### Target Configuration
- `--cpu CPU`, `-mcpu CPU`: Target microcontroller (**required**)

## Preprocessor Options

### Definitions
- `-D SYMBOL`, `--define SYMBOL`: Define preprocessor symbol
- `-U SYMBOL`, `--undefine SYMBOL`: Undefine preprocessor symbol

**Examples:**
```bash
# Define single symbols
xc8-wrapper cc --cpu PIC16F877A -D DEBUG

# Define with values
xc8-wrapper cc --cpu PIC16F877A -D _XTAL_FREQ=20000000 -D LED_PIN=0

# Multiple definitions
xc8-wrapper cc --cpu PIC16F877A -D DEBUG=1 -D VERSION=2 -D BOARD_REV=3
```

### Include Paths
- `-I PATH`: Add include directory

**Examples:**
```bash
# Single include path
xc8-wrapper cc --cpu PIC16F877A -I ./headers

# Multiple include paths
xc8-wrapper cc --cpu PIC16F877A -I ./include -I ./lib -I ../common
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
xc8-wrapper cc --cpu PIC16F877A -O0

# Size optimization (resource-constrained projects)
xc8-wrapper cc --cpu PIC16F877A -Os

# Speed optimization (performance-critical code)
xc8-wrapper cc --cpu PIC16F877A -O2
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
xc8-wrapper cc --cpu PIC16F877A --std c99

# Use C11 standard (default)
xc8-wrapper cc --cpu PIC16F877A --std c11
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

### Input Files
- `FILES...`: Source files to compile (C files, assembly files, object files)

### Output Control
- `-o FILE`: Specify output file name

### Output Files
- `-o FILE`: Output file name
- `--save-temps`: Do not delete intermediate files

**Examples:**
```bash
# Basic compilation with default output
xc8-wrapper cc --cpu PIC16F877A main.c

# Custom output file
xc8-wrapper cc --cpu PIC16F877A -o firmware.hex main.c

# Save intermediate files for debugging
xc8-wrapper cc --cpu PIC16F877A --save-temps main.c
```

## Common Command Patterns

### Development Workflow

**Quick compile (development):**
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 -O0 -v main.c
```

**Production build:**
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 -Os --std c99 main.c
```

**Debug build:**
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 -Og -D DEBUG=1 --save-temps main.c
```

### Project-Specific Examples

**Multi-file compilation:**
```bash
# Compile multiple source files
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c uart.c spi.c

# With custom includes and optimization
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
    -I ./include -I ./lib \
    -D VERSION=100 -O2 \
    main.c uart.c spi.c
```

### Testing and Validation

**Preprocessor output:**
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
    -E -C -H main.c
```

**Assembly generation:**
```bash
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
    -S -v main.c
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

**Solutions**:
1. **Use the cc subcommand**: `xc8-wrapper cc --cpu PIC16F877A`

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
- Solutions: Check file path, specify correct file name

### Debugging Tips

1. **Use verbose output**: Add `-v` to see detailed execution
2. **Check file paths**: Verify source files exist in current directory
3. **Validate XC8**: Test XC8 directly with `xc8-cc --version`
4. **Save intermediates**: Use `--save-temps` to inspect generated files

## Advanced Usage

### Custom XC8 Installation
```bash
# Using custom XC8 path
xc8-wrapper cc --xc8-path "/custom/path/to/xc8-cc" --cpu PIC16F877A main.c

# Multiple XC8 versions
xc8-wrapper cc --xc8-version 2.40 --cpu PIC16F877A main.c  # Legacy project
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A main.c  # Current project
```

### Integration with Build Systems

**Makefile integration:**
```makefile
CHIP = PIC16F877A
XC8_VERSION = 3.00

build:
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -O2 main.c

debug:
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -Og -D DEBUG=1 main.c
```

**Shell script integration:**
```bash
#!/bin/bash
set -e

CHIP="${1:-PIC16F877A}"
VERSION="${2:-3.00}"

echo "Building for $CHIP with XC8 $VERSION..."
xc8-wrapper cc --cpu "$CHIP" --xc8-version "$VERSION" -O2 main.c
echo "Build complete!"
```

## Related Documentation

- [Getting Started](getting-started.md) - Basic usage examples
- [Examples](examples.md) - Real-world usage scenarios
- [Development](development.md) - Development and contributing guide
- [FAQ](faq.md) - Frequently asked questions

### Passthrough Options
- `--passthrough STRING`, `-p STRING`: Pass options directly to xc8-cc without interpretation

**Examples:**
```bash
# Pass PIC-specific options not available in wrapper
xc8-wrapper cc --cpu PIC16F877A --passthrough="-mplib -gdwarf-3" main.c

# Pass multiple options with values
xc8-wrapper cc --cpu PIC16F877A --passthrough="-mchecksum=0x1234 --fill=0xFF" main.c

# Combine with regular options
xc8-wrapper cc --cpu PIC16F877A -O2 -v --passthrough="-mplib -mdownload-hex" main.c
```

**Security & Safety Notes:**

- Arguments are parsed using shell-like syntax (supports quotes and escaping)
- Use quotes for arguments containing spaces: `--passthrough='--output="my file.hex"'`
- Passthrough arguments are added after regular wrapper options
- Invalid passthrough syntax will cause compilation to fail

- **Security validation**: The following patterns are blocked for security:

  - Shell operators: `&`, `|`, `;`, `&&`, `||`, `>`, `<`, `>>`, `<<`
  - Command substitution: `` ` ``, `$(`, `${`
  - File traversal: `../`, `..\\`, `/etc/`, `\\windows\\`
  - Dangerous executables: `cmd.exe`, `powershell`, `bash`, `sh`, `rm`, `del`, `format`
- Only compiler-specific options should be passed through this mechanism
