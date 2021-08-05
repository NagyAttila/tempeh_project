#!/usr/bin/python
from __future__ import print_function # in case python2

import sys
import RPi.GPIO as GPIO
import signal
import time

## Setup
WARMER_PIN = 15

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(WARMER_PIN,GPIO.OUT)
GPIO.output(WARMER_PIN, GPIO.LOW)

## Main
print('Turn Off',end='\r')
GPIO.output(WARMER_PIN, GPIO.LOW)
