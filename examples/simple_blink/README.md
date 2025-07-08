# Simple Blink Example

This example demonstrates a simple LED blinking program for PIC16F876A.

## Features

- Configures PORTC as output
- Blinks all LEDs on PORTC with 500ms delay
- Uses proper configuration bits for PIC16F876A
- Demonstrates __delay_ms() function usage

## Configuration

- **Target**: PIC16F876A
- **Oscillator**: HS (High Speed) Crystal/Resonator
- **Frequency**: 4MHz
- **Watchdog**: Disabled
- **Power-up Timer**: Enabled
- **Brown-out Reset**: Enabled
- **Low Voltage Programming**: Disabled

## Compilation

To compile this example using xc8-wrapper:

```bash
# Compile to HEX file
xc8-wrapper cc --chip PIC16F876A --output main.hex main.c

# Or with optimization
xc8-wrapper cc --chip PIC16F876A --opt-level 1 --output main.hex main.c
```

## Testing

You can test the compilation without installing XC8 by running:

```bash
# Run compilation tests
pytest tests/test_compilation.py -v

# Check if XC8 is available
python install_xc8.py --check

# Install XC8 if needed (Linux/CI)
python install_xc8.py --install
```

## Hardware Setup

1. Connect LEDs to PORTC pins (RC0-RC7) through current-limiting resistors
2. Connect 4MHz crystal oscillator to OSC1/OSC2 pins
3. Ensure proper power supply connections (VDD, VSS)
4. Connect MCLR pin to VDD through 10kΩ resistor

## Expected Behavior

All LEDs connected to PORTC will blink simultaneously:
- 500ms ON
- 500ms OFF
- Continuous loop
