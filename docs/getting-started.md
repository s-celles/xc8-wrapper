# Getting Started

Step-by-step guide to get up and running with XC8 Wrapper.

This guide will walk you through creating your first PIC microcontroller project using XC8 Wrapper.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Your First Project](#your-first-project)
- [Common Usage Patterns](#common-usage-patterns)
- [Popular PIC Microcontrollers](#popular-pic-microcontrollers)
- [Project Templates](#project-templates)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, make sure you have:
- ✅ [XC8 Wrapper installed](installation.md)
- ✅ Microchip XC8 Compiler installed
- ✅ Basic knowledge of C programming

## Your First Project

Let's create a simple LED blink project for a PIC16F877A microcontroller.

### Step 1: Create Project Structure

```bash
mkdir my-pic-project
cd my-pic-project
mkdir src
mkdir build
```

### Step 2: Create Source Code

Create a file `src/main.c`:

```c
/*
 * Simple LED Blink Example
 * Target: PIC16F877A
 * LED connected to RB0
 */

#include <xc.h>

// Configuration bits
#pragma config FOSC = HS        // High Speed Oscillator
#pragma config WDTE = OFF       // Watchdog Timer Disabled
#pragma config PWRTE = ON       // Power-up Timer Enabled
#pragma config BOREN = ON       // Brown-out Reset Enabled
#pragma config LVP = OFF        // Low Voltage Programming Disabled
#pragma config CPD = OFF        // Data EEPROM Code Protection Disabled
#pragma config WRT = OFF        // Flash Program Memory Write Disabled
#pragma config CP = OFF         // Flash Program Memory Code Protection Disabled

#define _XTAL_FREQ 20000000     // 20MHz crystal

void main(void) {
    // Configure PORTB as output
    TRISB = 0x00;
    PORTB = 0x00;

    while(1) {
        PORTB = 0x01;           // Turn on LED (RB0)
        __delay_ms(500);        // Wait 500ms
        PORTB = 0x00;           // Turn off LED
        __delay_ms(500);        // Wait 500ms
    }
}
```

### Step 3: Compile with XC8 Wrapper

Now let's compile the project:

```bash
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A main.c
```

**Note:** XC8 Wrapper uses a colored logging system where:
- `[INFO]` messages (in white) show general information and successful operations
- `[WARNING]` messages (in yellow) indicate compilation steps and progress
- `[ERROR]` messages (in red) would show any compilation errors
- Timestamps help track the compilation process

If successful, you should see output like:

```
12:46:47 [INFO] === XC8 TOOLCHAIN WRAPPER ===
12:46:55 [INFO] ✓ XC8 cc v3.00 found
12:46:55 [INFO]
=== XC8 CC COMPILATION for PIC16F877A ===
12:46:55 [INFO] ✓ Source file found: src\main.c
12:46:55 [WARNING]
Compilation in progress...
12:46:55 [INFO] Configuration:
12:46:55 [INFO]   - Tool: XC8 CC (xc8-cc)
12:46:55 [INFO]   - Version: v3.00
12:46:55 [INFO]   - Target MCU: PIC16F877A
12:46:55 [INFO]   - Source: src\main.c
12:46:55 [INFO]   - Output: build\main.hex
12:46:55 [WARNING]
Step 1: Compiling main.c...
12:46:55 [WARNING] Compiling main.c...
12:46:55 [INFO] Command: "C:\Program Files\Microchip\xc8\v3.00\bin\xc8-cc.exe" -mcpu=PIC16F877A ...
[XC8 compiler output...]
12:46:55 [INFO] ✓ Compiling main.c successful
12:46:55 [WARNING]
Step 2: Linking...
12:46:55 [WARNING] Linking...
12:46:55 [INFO] Command: "C:\Program Files\Microchip\xc8\v3.00\bin\xc8-cc.exe" -mcpu=PIC16F877A ...
[XC8 linker output...]
12:46:55 [INFO] ✓ Linking successful
12:46:55 [INFO]
✓ HEX file generated: main.hex (309 bytes)
12:46:55 [INFO]
Generated files:
12:46:55 [INFO]   main.cmf - 9414 bytes
12:46:55 [INFO]   main.hex - 309 bytes
12:46:55 [INFO]   main.map - 10189 bytes
12:46:55 [INFO]   main.elf - 4350 bytes
12:46:55 [INFO]   [... and other build files]
12:46:55 [INFO]
🎉 SUCCESS! PIC PIC16F877A project compiled with XC8 CC v3.00!
12:46:55 [INFO] File ready for programming: build\main.hex
12:46:55 [INFO] Next step: Upload with upload script
```

### Step 4: Check Generated Files

Your project structure should now look like:

```
my-pic-project/
├── src/
│   └── main.c
├── build/
│   ├── main.hex          ← Programming file (Intel HEX format)
│   ├── main.elf          ← Executable and Linkable Format file
│   ├── main.p1           ← Compiled object file
│   ├── main.map          ← Memory map and symbol information
│   ├── main.cmf          ← Chip metadata file
│   ├── main.sym          ← Symbol table
│   ├── memoryfile.xml    ← Memory usage summary
│   ├── main.hxl          ← HEX file log
│   ├── main.s            ← Generated assembly code
│   └── startup.s         ← Startup code
```

The most important file is `main.hex` - this is what you'll upload to your PIC microcontroller.

## Common Usage Patterns

### Basic C Compilation

```bash
# Minimal command
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A main.c

# With custom directories (not currently supported - specify files directly)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A \
    -I ./include \
    src/main.c src/uart.c
```

### Assembly Programming

XC8 Wrapper also supports PIC assembly programming using the `as` (assembler) command:

```bash
# Basic assembly compilation
xc8-wrapper as --cpu PIC16F876A main.s

# With custom output file
xc8-wrapper as --cpu PIC16F876A -o output/firmware.hex main.s

# Verbose assembly output
xc8-wrapper as --cpu PIC16F876A -v main.s

# Assembly with listing and debug info
xc8-wrapper as --cpu PIC16F876A --passthrough="-list -map -g" main.s

# Intel HEX format output
xc8-wrapper as --cpu PIC18F4550 --passthrough="-inhx32" main.s
```

#### Assembly Example

Create a file `src/blink.s` for a simple LED blink in assembly:

```assembly
; LED Blink in PIC Assembly for PIC16F876A
PROCESSOR 16F876A

; Configuration bits
config FOSC=HS, WDTE=OFF, PWRTE=OFF, BOREN=ON, LVP=OFF, CPD=OFF, WRT=OFF, CP=OFF

; Register definitions
STATUS  equ 0x03
RP0     equ 5
TRISC   equ 0x87    ; Bank 1
PORTC   equ 0x07    ; Bank 0

; Variables
psect udata_shr,global,class=COMMON,space=1,delta=1,noexec
delay_count1: ds 1
delay_count2: ds 1

; Reset vector
psect resetVect,global,class=CODE,delta=2
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

Compile it with:

```bash
xc8-wrapper as --cpu PIC16F876A blink.s
```

For more advanced assembly options:

```bash
# With listing file and debug information
xc8-wrapper as --cpu PIC16F876A --passthrough="-list -map -g" blink.s

# Intel HEX format with verbose output
xc8-wrapper as --cpu PIC16F876A -v --passthrough="-inhx32" blink.s
```

### Optimization Options

```bash
# No optimization (fastest compile)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A -O0 main.c

# Size optimization (smallest code)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A -Os main.c

# Speed optimization
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A -O2 main.c
```

### Adding Preprocessor Definitions

```bash
# Define constants
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A \
    -D DEBUG=1 \
    -D LED_PIN=0 \
    -D _XTAL_FREQ=20000000 \
    main.c
```

### Including Header Paths

```bash
# Add include directories
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A \
    -I ./include \
    -I ./lib/headers \
    main.c
```

### Verbose Output

```bash
# See detailed compilation process
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A -v main.c
```

## Popular PIC Microcontrollers

Here are some commonly used PIC microcontrollers and their XC8 Wrapper commands:

### PIC16F Series
```bash
# PIC16F877A (40-pin, popular for learning)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F877A main.c

# PIC16F84A (18-pin, simple projects)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F84A main.c

# PIC16F628A (18-pin with more features)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC16F628A main.c
```

### PIC18F Series
```bash
# PIC18F4550 (USB-capable)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC18F4550 main.c

# PIC18F4520 (Enhanced mid-range)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC18F4520 main.c
```

### PIC12F Series
```bash
# PIC12F675 (8-pin, tiny projects)
xc8-wrapper cc --xc8-version 3.00 --cpu PIC12F675 main.c
```

## Project Templates

### Simple I/O Project
```c
#include <xc.h>

// Configuration bits for PIC16F877A
#pragma config FOSC = HS, WDTE = OFF, PWRTE = ON, BOREN = ON, LVP = OFF

#define _XTAL_FREQ 20000000

void main(void) {
    TRISB = 0x00;    // PORTB as output
    TRISD = 0xFF;    // PORTD as input

    while(1) {
        PORTB = PORTD;   // Copy input to output
        __delay_ms(10);  // Small delay
    }
}
```

### ADC Reading Project
```c
#include <xc.h>

#pragma config FOSC = HS, WDTE = OFF, PWRTE = ON, BOREN = ON, LVP = OFF

#define _XTAL_FREQ 20000000

unsigned int adc_read(unsigned char channel) {
    ADCON0 = (channel << 3) | 0x01;  // Select channel and turn on ADC
    __delay_us(30);                  // Acquisition time
    GO_nDONE = 1;                    // Start conversion
    while(GO_nDONE);                 // Wait for completion
    return ((ADRESH << 8) + ADRESL); // Return 10-bit result
}

void main(void) {
    ADCON1 = 0x0E;    // AN0 as analog input
    TRISA = 0x01;     // RA0 as input
    TRISB = 0x00;     // PORTB as output

    while(1) {
        unsigned int value = adc_read(0);  // Read AN0
        PORTB = value >> 2;                // Display upper 8 bits
        __delay_ms(100);
    }
}
```

## Next Steps

Now that you've successfully compiled your first project:

1. **Learn more commands**: Check the [CLI Reference](cli-reference.md)
2. **See more examples**: Browse [Examples](examples.md)
3. **Get help**: Read the [FAQ](faq.md) or [create an issue](https://github.com/s-celles/xc8-wrapper/issues)
4. **Programming**: Use your preferred PIC programmer to upload `main.hex`

## Troubleshooting

### Common Issues

**"Source file not found"**
- Check that your source file exists in the current directory
- Specify the correct source file: `xc8-wrapper cc --cpu PIC16F877A mysrc.c`

**"XC8 not found"**
- Verify XC8 installation: `xc8-cc --version`
- Use `--xc8-path` to specify custom location
- Check version format: use `3.00` not `3.0`

**"Compilation failed"**
- Check your C code for syntax errors
- Use `-v` to see detailed error messages
- Ensure proper configuration bits for your target MCU

**"CPU not supported"**
- Verify the exact CPU name with XC8 documentation
- Check case sensitivity: `PIC16F877A` not `pic16f877a`

Need more help? Check our [FAQ](faq.md) or [create an issue](https://github.com/s-celles/xc8-wrapper/issues).
