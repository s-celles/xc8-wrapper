---
layout: default
title: Getting Started
nav_order: 3
---

# Getting Started
{: .no_toc }

This guide will walk you through creating your first PIC microcontroller project using XC8 Wrapper.
{: .fs-6 .fw-300 }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

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
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A
```

If successful, you should see output like:

```
=== XC8 TOOLCHAIN WRAPPER ===

=== XC8 CC COMPILATION for PIC16F877A ===
✓ XC8 cc v3.00 found
✓ Source file found: src/main.c
✓ Created build directory: build

Compilation in progress...
Configuration:
  - Tool: XC8 CC (xc8-cc.exe)
  - Version: v3.00
  - Target MCU: PIC16F877A
  - Source: src/main.c
  - Output: build/main.hex

Step 1: Compiling main.c...
Command: "C:/Program Files/Microchip/xc8/v3.00/bin/xc8-cc.exe" "-mcpu=PIC16F877A" ...
✓ Compiling main.c successful

Step 2: Linking...
✓ Linking successful

✓ HEX file generated: main.hex (1234 bytes)

🎉 SUCCESS! PIC PIC16F877A project compiled with XC8 CC v3.00!
File ready for programming: build/main.hex
Next step: Upload with upload script
```

### Step 4: Check Generated Files

Your project structure should now look like:

```
my-pic-project/
├── src/
│   └── main.c
├── build/
│   ├── main.hex     ← Programming file
│   ├── main.elf     ← Executable file
│   ├── main.p1      ← Object file
│   ├── main.map     ← Memory map
│   └── memoryfile.xml ← Memory usage
```

## Common Usage Patterns

### Basic Compilation

```bash
# Minimal command
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A

# With custom directories
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A \
    --source-dir my_src \
    --build-dir my_build \
    --main-c-file my_main.c
```

### Optimization Options

```bash
# No optimization (fastest compile)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -O0

# Size optimization (smallest code)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -Os

# Speed optimization
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A -O2
```

### Adding Preprocessor Definitions

```bash
# Define constants
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A \
    -D DEBUG=1 \
    -D LED_PIN=0 \
    -D _XTAL_FREQ=20000000
```

### Including Header Paths

```bash
# Add include directories
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A \
    -I ./include \
    -I ./lib/headers
```

### Verbose Output

```bash
# See detailed compilation process
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A --verbose
```

## Popular PIC Microcontrollers

Here are some commonly used PIC microcontrollers and their XC8 Wrapper commands:

### PIC16F Series
```bash
# PIC16F877A (40-pin, popular for learning)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F877A

# PIC16F84A (18-pin, simple projects)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F84A

# PIC16F628A (18-pin with more features)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F628A
```

### PIC18F Series
```bash
# PIC18F4550 (USB-capable)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC18F4550

# PIC18F4520 (Enhanced mid-range)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC18F4520
```

### PIC12F Series
```bash
# PIC12F675 (8-pin, tiny projects)
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC12F675
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
3. **Configure your setup**: Read [Configuration](configuration.md)
4. **Programming**: Use your preferred PIC programmer to upload `main.hex`

## Troubleshooting

### Common Issues

**"Source file not found"**
- Check that `src/main.c` exists
- Use `--source-dir` and `--main-c-file` to specify different locations

**"XC8 not found"**
- Verify XC8 installation: `xc8-cc --version`
- Use `--xc8-path` to specify custom location
- Check version format: use `3.00` not `3.0`

**"Compilation failed"**
- Check your C code for syntax errors
- Use `--verbose` to see detailed error messages
- Ensure proper configuration bits for your target MCU

**"CPU not supported"**
- Verify the exact CPU name with XC8 documentation
- Check case sensitivity: `PIC16F877A` not `pic16f877a`

Need more help? Check our [FAQ](faq.md) or [create an issue](https://github.com/s-celles/xc8-wrapper/issues).
