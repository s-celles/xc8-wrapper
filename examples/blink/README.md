# Example: LED Blink

This project blinks LEDs connected to PORTC of a PIC16F876A.

## Compilation

```bash
cd /workspaces/xc8-wrapper/examples/blink
xc8-wrapper --tool cc --xc8-version 3.00 --cpu PIC16F876A --source-dir . --main-c-file main.c
```

## Configuration

- **MCU**: PIC16F876A
- **Oscillator**: 4MHz (HS)
- **LEDs**: Connected to PORTC (RC0-RC7)

## Generated Files

- `main.hex` - Hexadecimal file for programming
- `main.elf` - ELF file with debug information
