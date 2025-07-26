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

### Simple Assembly Project (PIC16F876A)

This example demonstrates basic assembly programming using the XC8 Wrapper assembler.

**Project Structure:**
```
my_asm_project/
├── src/
│   └── blink.s
└── build/
```

**blink.s:**
```assembly
; Simple LED blink in assembly for PIC16F876A
; LED connected to RC0

#include <xc.inc>

; Configuration bits
config FOSC = HS        ; High speed crystal
config WDTE = OFF       ; Watchdog timer disabled
config PWRTE = ON       ; Power-up timer enabled
config BOREN = ON       ; Brown-out reset enabled
config LVP = OFF        ; Low voltage programming disabled
config CPD = OFF        ; Data EEPROM code protection off
config WRT = OFF        ; Flash program memory write protection off
config CP = OFF         ; Flash program memory code protection off

; Variable declarations
psect udata_bank0
delay_count1: ds 1
delay_count2: ds 1

; Reset vector
psect reset_vec,global,class=CODE,delta=2
    pagesel MAIN
    goto    MAIN

; Main program
psect code,global,class=CODE,delta=2
MAIN:
    ; Set bank 1 for TRIS registers
    bsf STATUS, RP0
    clrf TRISC          ; PORTC as output
    bcf STATUS, RP0     ; Back to bank 0
    
    clrf PORTC          ; Initialize PORTC

MAIN_LOOP:
    bsf PORTC, 0        ; Turn on LED (RC0)
    call DELAY          ; Wait
    bcf PORTC, 0        ; Turn off LED
    call DELAY          ; Wait
    goto MAIN_LOOP      ; Repeat

DELAY:
    movlw 0xFF
    movwf delay_count1
DELAY_OUTER:
    movlw 0xFF
    movwf delay_count2
DELAY_INNER:
    decfsz delay_count2, f
    goto DELAY_INNER
    decfsz delay_count1, f
    goto DELAY_OUTER
    return

END
```

**Assembly:**
```bash
xc8-wrapper as --cpu PIC16F876A --xc8-version 3.00 blink.s
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

### Assembly Builds

```bash
# Debug assembly build with verbose output
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 \
    -v \
    --passthrough="-g -list -map" \
    main.s

# Optimized assembly build with Intel HEX output
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 \
    --passthrough="-inhx32 -map" \
    main.s

# Assembly with custom output file
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 \
    -o firmware.hex \
    main.s
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

# Source files
C_SOURCES = main.c uart.c
ASM_SOURCES = startup.s interrupts.s

# Default target
all: build

# Build C project
build:
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -O2 $(C_SOURCES)

# Build assembly project
build-asm:
	xc8-wrapper as --cpu $(CHIP) --xc8-version $(XC8_VERSION) $(ASM_SOURCES)

# Debug targets
debug:
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -Og -D DEBUG=1 $(C_SOURCES)

debug-asm:
	xc8-wrapper as --cpu $(CHIP) --xc8-version $(XC8_VERSION) \
		--passthrough="-g -list -map" $(ASM_SOURCES)

# Clean target
clean:
	rm -rf build/

# Release target
release: clean
	xc8-wrapper cc --cpu $(CHIP) --xc8-version $(XC8_VERSION) -Os $(C_SOURCES)

.PHONY: all build build-asm debug debug-asm clean release
```

### Batch Script (Windows)

```batch
@echo off
setlocal

set CHIP=PIC16F877A
set XC8_VERSION=3.00
set PROJECT_NAME=my_project
set BUILD_TYPE=%1

if "%BUILD_TYPE%"=="" set BUILD_TYPE=c

echo Building %PROJECT_NAME% for %CHIP%...

if "%BUILD_TYPE%"=="asm" (
    echo Building assembly project...
    xc8-wrapper as --cpu %CHIP% --xc8-version %XC8_VERSION% -v main.s
) else (
    echo Building C project...
    xc8-wrapper cc --cpu %CHIP% --xc8-version %XC8_VERSION% -O2 -v main.c
)

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
BUILD_TYPE="${3:-c}"
PROJECT_NAME="my_project"

echo "Building $PROJECT_NAME for $CHIP with XC8 v$XC8_VERSION..."

if [ "$BUILD_TYPE" = "asm" ]; then
    echo "Building assembly project..."
    xc8-wrapper as --cpu "$CHIP" --xc8-version "$XC8_VERSION" -v main.s
else
    echo "Building C project..."
    xc8-wrapper cc --cpu "$CHIP" --xc8-version "$XC8_VERSION" -O2 -v main.c
fi

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
        # Build C firmware
        xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c -O2
        
        # Build assembly firmware (if present)
        if [ -f main.s ]; then
          xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 main.s
        fi

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

**Issue: PIC-AS not found**
```bash
# Check if PIC-AS is installed
xc8-wrapper as --cpu PIC16F877A --pic-as-help

# Use specific path
xc8-wrapper as --cpu PIC16F877A \
    --xc8-path "/path/to/pic-as"
```

**Issue: Compilation errors**
```bash
# Enable verbose output for debugging
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 main.c \
    -v \
    --save-temps
```

**Issue: Assembly errors**
```bash
# Enable verbose output for assembly debugging
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 main.s \
    -v \
    --passthrough="-list -map"
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

## Passthrough Examples

### Using Unsupported XC8 Options

XC8 has many specialized options that aren't directly supported by the wrapper. Use `--passthrough` to access them:

```bash
# PIC library support
xc8-wrapper cc --cpu PIC18F4550 --passthrough="-mplib" main.c

# Debug format options
xc8-wrapper cc --cpu PIC16F877A --passthrough="-gdwarf-3" main.c

# Memory configuration
xc8-wrapper cc --cpu PIC16F877A --passthrough="--fill=0xFF --memorysummary=memory.xml" main.c

# Device-specific options
xc8-wrapper cc --cpu PIC16F877A --passthrough="-mdownload-hex -mresetbits -mconfig" main.c
```

### Using Unsupported PIC-AS Options

PIC-AS assembler has many specialized options for assembly projects. Use `--passthrough` to access them:

```bash
# Generate listing file and map
xc8-wrapper as --cpu PIC16F877A --passthrough="-list -map" main.s

# Intel HEX output format
xc8-wrapper as --cpu PIC18F4550 --passthrough="-inhx32" main.s

# Debug information in assembly
xc8-wrapper as --cpu PIC16F877A --passthrough="-g -gdwarf-3" main.s

# PIC14 family specific options
xc8-wrapper as --cpu PIC16F877A --passthrough="-mpic14 -msummary" main.s

# PIC18 family specific options  
xc8-wrapper as --cpu PIC18F4550 --passthrough="-mpic16 -mwarn=3" main.s
```

### Complex Passthrough Examples

```bash
# Production build with checksums and memory configuration
xc8-wrapper cc --cpu PIC18F4550 --xc8-version 3.00 \
    -Os \
    --passthrough="-mplib -mdownload-hex -mchecksum=0x1234 --fill=0xFF" \
    main.c

# Debug build with advanced debugging features
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
    -Og -D DEBUG=1 \
    --passthrough="-gdwarf-3 --memorysummary=debug_memory.xml" \
    main.c

# Custom serial number and device configuration
xc8-wrapper cc --cpu PIC16F877A \
    --passthrough='-mserial="ABC123" -mconfig -mosccal' \
    main.c

# Assembly with comprehensive output and debugging
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 \
    --passthrough="-list -map -g -gdwarf-3 -inhx32" \
    main.s

# Assembly production build with optimization markers
xc8-wrapper as --cpu PIC18F4550 --xc8-version 3.00 \
    --passthrough="-mpic16 -mwarn=0 -inhx32 -map" \
    production.s
```

### Combining Regular and Passthrough Options

```bash
# Mix wrapper options with specialized XC8 options
xc8-wrapper cc --cpu PIC18F4550 --xc8-version 3.00 \
    -O2 -v \
    -I ./include -I ./lib \
    -D DEBUG=0 -D VERSION=100 \
    --passthrough="-mplib -gdwarf-3 -mdownload-hex" \
    src/main.c src/uart.c src/spi.c

# Mix assembly wrapper options with specialized PIC-AS options
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 \
    -v \
    -o firmware.hex \
    --passthrough="-list -map -g" \
    src/main.s src/interrupts.s
```

### Security Considerations

The `--passthrough` option includes security validation to prevent potentially dangerous commands:

```bash
# ❌ These will be blocked for security
xc8-wrapper cc --cpu PIC16F877A --passthrough "& echo hacked" main.c
xc8-wrapper cc --cpu PIC16F877A --passthrough "; rm -rf /" main.c
xc8-wrapper cc --cpu PIC16F877A --passthrough "|cat /etc/passwd" main.c

# ✅ These are safe and allowed
xc8-wrapper cc --cpu PIC16F877A --passthrough "-mplib -gdwarf-3" main.c
xc8-wrapper cc --cpu PIC16F877A --passthrough "--fill=0xFF" main.c
```

**Blocked patterns include:**
- Shell operators: `&`, `|`, `;`, `&&`, `||`, `>`, `<`
- Command substitution: `` ` ``, `$(`, `${`
- File traversal: `../`, `..\\`, `/etc/`, `\\windows\\`
- Dangerous commands: `cmd.exe`, `powershell`, `bash`, `rm`, `del`

This ensures that only legitimate compiler options can be passed through.

### Error Handling

If you pass invalid options through `--passthrough`, XC8 or PIC-AS will report the error:

```bash
# This will fail with XC8 error
xc8-wrapper cc --cpu PIC16F877A --xc8-version 3.00 \
    --passthrough "-invalid-option" main.c

# This will fail with PIC-AS error
xc8-wrapper as --cpu PIC16F877A --xc8-version 3.00 \
    --passthrough "-invalid-asm-option" main.s
```

The wrapper will show the XC8 or PIC-AS error message to help you identify the problem.

## Next Steps

- Check out the [CLI Reference](cli-reference.md) for complete command documentation
- Read the [Getting Started](getting-started.md) guide for step-by-step tutorials
- Visit the [FAQ](faq.md) for answers to common questions
