#!/usr/bin/python
from __future__ import print_function # in case python2

import sys
import RPi.GPIO as GPIO
import signal
import time

## Functions
def exit_gracefully(signum, frame):
    # In case we get another SIGINT signal during this function
    signal.signal(signal.SIGINT, original_sigint)

    # Turn off the used GPIO pins
    GPIO.output(WARMER_PIN, GPIO.LOW)

    print('\nBye bye :)')
    sys.exit(1)


## Setup
WARMER_PIN = 18

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(WARMER_PIN,GPIO.OUT)
GPIO.output(WARMER_PIN, GPIO.LOW)

# replace SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)

## Main
toggle = True
while True:
    if toggle == True:
        print('Turn On ',end='\r')
        GPIO.output(WARMER_PIN, GPIO.HIGH)
        toggle = False
    else:
        print('Turn Off',end='\r')
        GPIO.output(WARMER_PIN, GPIO.LOW)
        toggle = True
    time.sleep(1)
