#!/usr/bin/env python3
"""
Print to a ti745 terminal that's controlled via a relay

by default the serial pin is on port 7, and the relay is on port 3
override these with environment variables DTR_PIN and RELAY_PIN

prints from stdin, so pipes work well:
    cowsay "James is super cool" | ti_print
"""
import sys
import time
import serial
import os
import traceback

import RPi.GPIO as GPIO

dtr_pin = os.environ.get("DTR_PIN", 7)
relay_pin = os.environ.get("RELAY_PIN", 3)
serial_port = os.environ.get("TI_SERIAL", "/dev/ttyAMA0")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(dtr_pin, GPIO.IN)  # terminal DTR
GPIO.setup(relay_pin, GPIO.OUT)  # relay connection

def set_relay(state):
    print(f"Turning relay to {state}")
    GPIO.output(relay_pin, state)

def dtr_state():
    return GPIO.input(dtr_pin)

def encode_line(line):
    '''encodes a string into a format the terminal can understand
    e.g. replacing newlines with CLRF, replacing scandic characters'''
    line = line.replace("\n", "\r\n")
    line = line.upper()
    return line


def print_stdin():
    '''sends stdin to the terminal'''
    serialPort = serial.Serial(port=serial_port,
                            timeout = 2,
                            baudrate=300,
                            parity=serial.PARITY_EVEN,
                            bytesize=serial.SEVENBITS,
                            stopbits=serial.STOPBITS_ONE)

    serialPort.flushInput()
    serialPort.flushOutput()

    for line in sys.stdin:
        line = encode_line(line)
        print(line, end="")
        serialPort.write(line.encode())
        serialPort.flush()

    serialPort.close()


def main(on_time=2, print_delay=2, endprint_delay=2):
    try:
        set_relay(True)
        time.sleep(on_time)
        if dtr_state():
            print("Terminal online")
            time.sleep(print_delay)
            print_stdin()
            time.sleep(endprint_delay)
        else:
            print("terminal bounced")
    finally:
        set_relay(False)


if __name__ == "__main__":
    main()
