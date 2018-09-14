#!/usr/bin/python
from __future__ import print_function

import sys
import Adafruit_DHT
import numpy as np
import datetime as dt
import RPi.GPIO as GPIO


## Setup
TEMPERATURE_PIN = 4
WARMER_PIN = 18
DHT_VERSION = 11
N_MEASUREMENTS = 3
PRINT_SEPARATOR = ','

TRIGGER_TEMPERATURE = 28

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(WARMER_PIN,GPIO.OUT)
GPIO.output(WARMER_PIN, GPIO.LOW)


## Functions
def read_temperature():
    return Adafruit_DHT.read_retry(DHT_VERSION, TEMPERATURE_PIN)


## Main
print('DateTime', 'Temperature[C]','Humidity[%]', sep=PRINT_SEPARATOR)
while True:

    # 1: Read Sensor
    temperatures = []
    humidities = []
    for i in range(1,N_MEASUREMENTS+1):
        print('Reading Sensor data: ',i, '/', N_MEASUREMENTS, '\r',end='',sep='')
        sys.stdout.flush()
        humidity, temperature = read_temperature()
        humidities.append(humidity)
        temperatures.append(temperature)
    print('\r',end='')

    mean_temperature = np.average(temperatures)
    mean_humidity = np.average(humidities)

    # 2: Print Measurement
    print( dt.datetime.now(),
          '{0:0.1f}'.format(mean_temperature),
          '{0:0.1f}'.format(mean_humidity),
          sep=PRINT_SEPARATOR)

    # 3: Trun On/Off Warmer
    if mean_temperature < TRIGGER_TEMPERATURE:
        GPIO.output(WARMER_PIN, GPIO.HIGH)
    else:
        GPIO.output(WARMER_PIN, GPIO.LOW)

