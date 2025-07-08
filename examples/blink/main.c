#include <xc.h>

// Configuration bits for PIC16F876A
#pragma config FOSC = HS        // HS Oscillator
#pragma config WDTE = OFF       // Watchdog Timer disabled
#pragma config PWRTE = ON       // Power-up Timer enabled
#pragma config BOREN = ON       // Brown-out Reset enabled
#pragma config LVP = OFF        // Low Voltage Programming disabled
#pragma config CPD = OFF        // Data EEPROM Code Protection disabled
#pragma config WRT = OFF        // Flash Program Memory Write Enable disabled
#pragma config CP = OFF         // Flash Program Memory Code Protection disabled

#define _XTAL_FREQ 4000000      // Oscillator frequency 4MHz

void main(void) {
    // Configure PORTC as output
    TRISC = 0x00;

    while(1) {
        // Turn on all LEDs on PORTC
        PORTC = 0xFF;
        __delay_ms(500);

        // Turn off all LEDs
        PORTC = 0x00;
        __delay_ms(500);
    }
}
