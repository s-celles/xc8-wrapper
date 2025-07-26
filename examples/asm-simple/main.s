/**
 * @file main.s
 * @brief PIC 16F876A LED Blinking Project
 * @details Assembly code for LED blinking using Timer0
 * @author Generated Code
 * @date 2025
 * @version 1.0
 * 
 * @brief Main features:
 * - LED blinking on PORTC RC2 every 500ms
 * - Uses Timer0 with prescaler 1:256 for timing
 * - External 4MHz crystal oscillator
 * - Port configuration with detailed documentation
 * 
 * @note Hardware requirements:
 * - PIC16F876A microcontroller
 * - 4MHz crystal with 22pF capacitors
 * - LED with series resistor on RC2
 * - 5V power supply
 * 
 * @warning Ensure proper crystal connections for reliable operation
 */

; PIC 16F876A Project - LED Blinking with External Oscillator
; LED Blinking on PORTC RC2 every 500ms
    PROCESSOR 16F876A
    #include <xc.inc>

/**
 * @brief Configuration bits for PIC16F876A
 * @details Sets oscillator and protection settings
 * @param FOSC: HS = High Speed external crystal (4MHz)
 * @param WDTE: OFF = Watchdog timer disabled
 * @param PWRTE: OFF = Power-up timer disabled
 * @param BOREN: ON = Brown-out reset enabled
 * @param LVP: OFF = Low voltage programming disabled
 * @param CPD: OFF = Data EEPROM code protection disabled
 * @param WRT: OFF = Flash write protection disabled
 * @param CP: OFF = Code protection disabled
 */
; Configuration bits - EXTERNAL 4MHz CRYSTAL
    CONFIG FOSC=HS, WDTE=OFF, PWRTE=OFF, BOREN=ON, LVP=OFF, CPD=OFF, WRT=OFF, CP=OFF

/**
 * @brief Variable definitions in bank 0
 * @details RAM variables used by the application
 * @note Located in unbanked RAM for easy access
 */
; Variable definitions
PSECT udata_bank0
OVERFLOW_COUNT: DS 1        ; Counter for Timer0 overflows

/**
 * @brief LED pin definitions
 * @details Define bit positions for each LED on their respective ports
 * @note These constants define which bit to manipulate for each LED
 */
; LED constants definitions
/** @brief LED 4 connected to port C bit 2 */
LED4        EQU     2       ; RC2 (bit 2 of PORTC)
/** @brief LED 3 connected to port C bit 1 */
LED3        EQU     1       ; RC1 (bit 1 of PORTC)
/** @brief LED 2 connected to port C bit 0 */
LED2        EQU     0       ; RC0 (bit 0 of PORTC)
/** @brief LED 1 connected to port A bit 5 */
LED1        EQU     5       ; RA5 (bit 5 of PORTA)
/** @brief LED 0 connected to port A bit 3 */
LED0        EQU     3       ; RA3 (bit 3 of PORTA)

/**
 * @brief Reset vector
 * @details Program entry point after reset
 * @note PAGESEL ensures correct page for GOTO instruction
 * @warning Critical for proper startup
 */
; Reset vector
PSECT resetVect,class=CODE,delta=2
    PAGESEL MAIN
    GOTO    MAIN

/**
 * @brief Main program section
 * @details Contains all application code
 * @note Uses PSECT code for program memory placement
 */
; Main program
PSECT code,class=CODE,delta=2
MAIN:
    ; Port configuration
    BANKSEL TRISC
    
    /**
     * @brief Port C configuration
     * @details Must account for LEDs and system signals
     * @todo Define directions according to actual wiring
     * @note TRISC = 0b00100000 - Configuration to be completed according to wiring
     */
    MOVLW   0b00100000     ; RC5 input, others output
    MOVWF   TRISC
    
    /**
     * @brief Port A configuration
     * @details Must account for LEDs, push buttons and MONO signal
     * @todo Define directions according to actual wiring
     * @note Push buttons require pull-up resistors
     * @note TRISA = 0b00010110 - Configuration to be completed according to wiring
     */
    MOVLW   0b00010110     ; RA1, RA2, RA4 inputs, others output
    MOVWF   TRISA
    
    /**
     * @brief Port B configuration
     * @details Configuration according to system needs
     * @todo Verify if port B is used in this project
     * @note TRISB = 0b00000000 - Configuration to be completed according to wiring
     */
    MOVLW   0b00000000     ; All PORTB outputs
    MOVWF   TRISB
    
    /**
     * @brief Analog-to-digital converter configuration
     * @details Configure pins as digital or analog inputs
     * @todo Define which pins are analog/digital
     * @warning Default value may cause reading problems
     * @note ADCON1 = 0b00000110 - Configuration to be completed according to wiring
     */
    MOVLW   0b00000110     ; Disable ADC, all digital
    MOVWF   ADCON1
    
    /**
     * @brief Timer0 configuration
     * @details Configure Timer0 for timing delays
     * @note OPTION_REG = 0b10000111
     * @param Bit 7: RBPU = 1 (PORTB pull-ups disabled)
     * @param Bit 6: INTEDG = 0 (interrupt on falling edge)
     * @param Bit 5: T0CS = 0 (Timer0 clock = internal)
     * @param Bit 4: T0SE = 0 (Timer0 increment on low-to-high)
     * @param Bit 3: PSA = 0 (prescaler assigned to Timer0)
     * @param Bits 2-0: PS2:PS0 = 111 (prescaler 1:256)
     * @warning Prescaler affects timing calculations
     */
    MOVLW   0b10000111     ; Prescaler 1:256
    MOVWF   OPTION_REG
    
    /**
     * @brief Port initialization
     * @details Initialize all ports to known state
     * @note Clear all output latches
     */
    ; Switch to bank 0
    BANKSEL PORTC
    
    ; Clear all ports
    CLRF    PORTC
    CLRF    PORTA

/**
 * @brief Main application loop
 * @details Infinite loop that blinks LED4 (RC2) every 500ms
 * @note Uses LED4 constant for bit manipulation
 * @warning Loop runs indefinitely
 * @todo Expand to sequence through all LEDs
 */
MAIN_LOOP:
    ; Turn ON LED4 (RC2)
    BSF     PORTC, LED4     ; Using LED4 constant (bit 2)
    CALL    DELAY_500MS
    
    ; Turn OFF LED4 (RC2)
    BCF     PORTC, LED4     ; Using LED4 constant (bit 2)
    CALL    DELAY_500MS
    
    GOTO    MAIN_LOOP

/**
 * @brief 500ms delay function using Timer0
 * @details Uses Timer0 with prescaler 1:256 for timing
 * @note External crystal 4MHz, prescaler 1:256
 * @note Timer0 overflow every ~65ms, so need ~8 overflows
 * @param OVERFLOW_COUNT: Number of Timer0 overflows to wait
 * @return None
 * @warning Timing depends on oscillator frequency
 */
DELAY_500MS:
    MOVLW   8               ; 8 overflows for ~500ms
    MOVWF   OVERFLOW_COUNT
    
/**
 * @brief Timer0 overflow counting loop
 * @details Wait for specified number of Timer0 overflows
 * @note Each overflow = ~65.536ms with 4MHz crystal and 1:256 prescaler
 * @param TMR0: Timer0 register (cleared each iteration)
 * @param TMR0IF: Timer0 interrupt flag (bit 2 of INTCON)
 */
TIMER_LOOP:
    CLRF    TMR0            ; Clear Timer0
    BCF     INTCON, 2       ; Clear TMR0IF flag

/**
 * @brief Wait for Timer0 overflow
 * @details Polls TMR0IF flag until Timer0 overflows
 * @note Blocking wait - CPU does nothing else
 * @warning This is a polling loop, not interrupt-driven
 */
WAIT_OVERFLOW:
    BTFSS   INTCON, 2       ; Check TMR0IF flag
    GOTO    WAIT_OVERFLOW
    
    DECFSZ  OVERFLOW_COUNT, F
    GOTO    TIMER_LOOP
    
    RETURN

/**
 * @brief Example function - Turn on all LEDs
 * @details Demonstrates how to control all 5 LEDs
 * @note This function is not called in main loop - for reference only
 * @warning Ensure proper current limiting resistors for all LEDs
 */
ALL_LEDS_ON:
    BSF     PORTC, LED4     ; Turn on LED4 (RC2)
    BSF     PORTC, LED3     ; Turn on LED3 (RC1)
    BSF     PORTC, LED2     ; Turn on LED2 (RC0)
    BSF     PORTA, LED1     ; Turn on LED1 (RA5)
    BSF     PORTA, LED0     ; Turn on LED0 (RA3)
    RETURN

/**
 * @brief Example function - Turn off all LEDs
 * @details Demonstrates how to turn off all 5 LEDs
 * @note This function is not called in main loop - for reference only
 */
ALL_LEDS_OFF:
    BCF     PORTC, LED4     ; Turn off LED4 (RC2)
    BCF     PORTC, LED3     ; Turn off LED3 (RC1)
    BCF     PORTC, LED2     ; Turn off LED2 (RC0)
    BCF     PORTA, LED1     ; Turn off LED1 (RA5)
    BCF     PORTA, LED0     ; Turn off LED0 (RA3)
    RETURN

    END
