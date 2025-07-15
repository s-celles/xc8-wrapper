# Examples

Real-world usage examples and patterns for XC8 Wrapper.

## Basic Examples

### Simple LED Blink (PIC16F876A)

This example demonstrates the most basic usage - compiling a simple LED blink program.

**Project Structure:**
```
my_project/
├── src/
│   └── main.c
└── build/
```

**main.c:**
```c
#include <xc.h>

// Configuration bits
#pragma config FOSC = HS        // High speed crystal
#pragma config WDTE = OFF       // Watchdog timer disabled
#pragma config PWRTE = ON       // Power-up timer enabled
#pragma config BOREN = ON       // Brown-out reset enabled
#pragma config LVP = OFF        // Low voltage programming disabled
#pragma config CPD = OFF        // Data EEPROM code protection off
#pragma config WRT = OFF        // Flash program memory write protection off
#pragma config CP = OFF         // Flash program memory code protection off

#define _XTAL_FREQ 20000000     // 20MHz crystal

int main(void) {
    TRISB0 = 0;                 // Set RB0 as output (LED)

    while(1) {
        RB0 = 1;                // LED on
        __delay_ms(500);        // Wait 500ms
        RB0 = 0;                // LED off
        __delay_ms(500);        // Wait 500ms
    }

    return 0;
}
```

**Compilation:**
```bash
xc8-wrapper cc --cpu PIC16F876A --xc8-version 3.00 main.c
```

### Advanced Project with Custom Paths

**Project Structure:**
```
advanced_project/
├── firmware/
│   ├── main.c
│   ├── uart.c
│   └── uart.h
├── include/
│   └── config.h
├── output/
└── lib/
    └── common.h
```

**Compilation:**
```bash
xc8-wrapper cc --cpu PIC18F4550 --xc8-version 3.00 \
    -I ./include \
    -I ./lib \
    -D DEBUG=1 \
    -D VERSION=100 \
    -O2 \
    firmware/main.c firmware/uart.c
```
    -v
```

## Platform-Specific Examples

### Windows Development

```bash
# Using specific XC8 version
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c

# Using custom XC8 path
xc8-wrapper cc --cpu PIC16F877A \
    --xc8-path "C:\Program Files\Microchip\xc8\v3.00\bin\xc8-cc.exe"
```

### Linux/macOS Development

```bash
# Standard installation path detection
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c

# Custom installation
xc8-wrapper cc --cpu PIC16F877A \
    --xc8-path "/opt/microchip/xc8/v3.00/bin/xc8-cc"
```

## Development Workflow Examples

### Debug Build

```bash
# Debug configuration with verbose output
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c \
    -Og \
    -D DEBUG=1 \
    -D _DEBUG=1 \
    --save-temps \
    -v
```

### Release Build

```bash
# Optimized release build
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c \
    -Os \
    -D NDEBUG=1 \
    --std c99
```

### Production Build with Custom Output

```bash
# Production build with custom file names
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c \
    -O2 \
    --output-hex firmware_v1.0.hex \
    --output-elf firmware_v1.0.elf \
    --output-map firmware_v1.0.map
```

## Integration Examples

### Makefile Integration

```makefile
# Makefile for XC8 Wrapper projects
PROJECT = my_project
CHIP = PIC16F877A
XC8_VERSION = 3.00

# Default target
all: build

# Build target
build:
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -O2

# Debug target
debug:
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -Og -D DEBUG=1

# Clean target
clean:
	rm -rf build/

# Release target
release: clean
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -Os

.PHONY: all build debug clean release
```

### Batch Script (Windows)

```batch
@echo off
setlocal

set CHIP=PIC16F877A
set XC8_VERSION=3.00
set PROJECT_NAME=my_project

echo Building %PROJECT_NAME% for %CHIP%...

xc8-wrapper cc --cpu %CHIP% --xc8-version %XC8_VERSION% -O2 -v main.c

if %ERRORLEVEL% equ 0 (
    echo Build successful!
    echo Output files:
    dir build\*.hex
) else (
    echo Build failed with error %ERRORLEVEL%
    exit /b 1
)

pause
```

### Shell Script (Linux/macOS)

```bash
#!/bin/bash
set -e

CHIP="${1:-PIC16F877A}"
XC8_VERSION="${2:-3.00}"
PROJECT_NAME="my_project"

echo "Building $PROJECT_NAME for $CHIP with XC8 v$XC8_VERSION..."

xc8-wrapper cc --cpu "$CHIP" --xc8-version "$XC8_VERSION" -O2 -v main.c

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "Output files:"
    ls -la build/*.hex 2>/dev/null || echo "No HEX files found"
else
    echo "❌ Build failed!"
    exit 1
fi
```

## CI/CD Examples

### GitHub Actions

```yaml
name: Build Firmware

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install XC8 Wrapper
      run: pip install xc8-wrapper

    - name: Install XC8 Compiler
      run: |
        # Download and install XC8 compiler
        # (Implementation depends on your setup)

    - name: Build firmware
      run: |
        xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -O2

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: firmware
        path: build/*.hex
```

## Troubleshooting Examples

### Common Issues and Solutions

**Issue: XC8 not found**
```bash
# Check if XC8 is installed
xc8-wrapper cc --cpu PIC16F877A --help

# Use specific path
xc8-wrapper cc --cpu PIC16F877A \
    --xc8-path "/path/to/xc8-cc"
```

**Issue: Compilation errors**
```bash
# Enable verbose output for debugging
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c \
    -v \
    --save-temps
```

**Issue: Custom include paths**
```bash
# Add multiple include directories
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c \
    -I ./include \
    -I ./lib \
    -I ../common
```

## Performance Examples

### Optimization Levels

```bash
# No optimization (fastest compilation)
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -O0

# Basic optimization
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -O1

# Standard optimization (recommended)
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -O2

# Aggressive optimization
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -O3

# Size optimization (for resource-constrained devices)
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -Os

# Debug-friendly optimization
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -Og
```

## Next Steps

- Check out the [CLI Reference](cli-reference.md) for complete command documentation
- Read the [Getting Started](getting-started.md) guide for step-by-step tutorials
- Visit the [FAQ](faq.md) for answers to common questions

