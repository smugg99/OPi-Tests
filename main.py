#!/usr/bin/env python3

import wiringpi as GPIO
import smbus
import time

# Define DS1302 pins (using wPi numbering)
RST = 7  # wPi pin for RST
DAT = 0  # wPi pin for DAT
CLK = 6  # wPi pin for CLK

# Set up GPIO
GPIO.wiringPiSetup()
GPIO.pinMode(RST, GPIO.OUTPUT)
GPIO.pinMode(DAT, GPIO.OUTPUT)
GPIO.pinMode(CLK, GPIO.OUTPUT)

# Set up I2C
bus = smbus.SMBus(1)  # Use bus 1 for Orange Pi

def send_byte(byte):
    bits = [int(bit) for bit in bin(byte)[2:].zfill(8)]
    GPIO.digitalWrite(DAT, GPIO.HIGH)
    for bit in bits:
        GPIO.digitalWrite(CLK, GPIO.LOW)
        GPIO.digitalWrite(DAT, bit)
        GPIO.digitalWrite(CLK, GPIO.HIGH)

def read_byte():
    bits = []
    GPIO.digitalWrite(DAT, GPIO.HIGH)
    for _ in range(8):
        GPIO.digitalWrite(CLK, GPIO.LOW)
        bits.append(GPIO.digitalRead(DAT))
        GPIO.digitalWrite(CLK, GPIO.HIGH)
    return int(''.join(map(str, bits)), 2)

def write_command(command):
    GPIO.digitalWrite(RST, GPIO.LOW)
    send_byte(command)
    GPIO.digitalWrite(RST, GPIO.HIGH)

def read_time():
    write_command(0xBF)
    time.sleep(0.000001)  # Wait for the DS1302 to be ready
    return [read_byte() for _ in range(7)]

def format_time(time_data):
    return f"{time_data[6] + 2000}-{time_data[5]:02d}-{time_data[4]:02d} " \
           f"{time_data[2]:02d}:{time_data[1]:02d}:{time_data[0]:02d}"

try:
    while True:
        current_time = read_time()
        formatted_time = format_time(current_time)
        print(f"Current Time: {formatted_time}")
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgram terminated by user.")
    GPIO.digitalWrite(RST, GPIO.HIGH)  # Ensure RST is set to HIGH on exit
    GPIO.cleanup()
