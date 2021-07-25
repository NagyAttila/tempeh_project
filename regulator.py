#!/usr/bin/python3
from __future__ import print_function

import sys
import numpy as np
import datetime as dt
import RPi.GPIO as GPIO
import signal
import glob
import time
import os

## Setup
WARMER_PIN = 14
N_MEASUREMENTS = 10
PRINT_SEPARATOR = ','
MEASUREMENT_PERIOD = 60

MIN_TEMPERATURE = 32

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(WARMER_PIN,GPIO.OUT)
GPIO.output(WARMER_PIN, GPIO.LOW)

# DS18B20 Sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        # temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

## Functions
def read_temperature():
    return read_temp()

def exit_gracefully(signum, frame):
    # In case we get another SIGINT signal during this function
    signal.signal(signal.SIGINT, original_sigint)

    # Turn off the used GPIO pins
    GPIO.output(WARMER_PIN, GPIO.LOW)

    print('\nBye bye :)')
    sys.exit(1)

def reboot():
    os.system('sudo reboot')

## Main

# replace SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)
prev_heater_on = False

print('DateTime', 'DS18B20-Temperature[C]', 'HeaterOn', sep=PRINT_SEPARATOR)
while True:

    start_time = time.time()
    # 1: Read Sensor
    temperatures = []
    ds18b20_error = False

    for i in range(1,N_MEASUREMENTS+1):
        sys.stdout.flush()
        try:
            temperature = read_temperature()
            temperatures.append(temperature)
        except Exception as e:
            ds18b20_error = True

    if ds18b20_error or None in temperatures:
        print('Connect DS18B20 Cables Properly!')
        # TODO: signal error somehow
        continue

    mean_temperature = np.average(temperatures)

    heater_on = mean_temperature < MIN_TEMPERATURE
    prev_heater_on = heater_on

    # 2: Print Measurement
    print( dt.datetime.now(),
          '{0:0.1f}'.format(mean_temperature),
          '{0:0.1f}'.format(heater_on),
          sep=PRINT_SEPARATOR)

    # 3: Trun On/Off Warmer
    if heater_on:
        # Reverse logic due to opto-coupling
        GPIO.output(WARMER_PIN, GPIO.LOW)
    else:
        GPIO.output(WARMER_PIN, GPIO.HIGH)

    end_time = time.time()
    time_delta = (end_time - start_time)
    if time_delta < MEASUREMENT_PERIOD:
        time.sleep(MEASUREMENT_PERIOD - time_delta)

