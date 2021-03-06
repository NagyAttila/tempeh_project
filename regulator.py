#!/usr/bin/python3
from __future__ import print_function

import sys
import Adafruit_DHT
import numpy as np
import datetime as dt
import RPi.GPIO as GPIO
import signal
import glob
import time
import os

## Setup
DHT11_TEMPERATURE_PIN = 18
WARMER_PIN = 14
DHT11_VERSION = 11
N_MEASUREMENTS = 10
PRINT_SEPARATOR = ','
MEASUREMENT_PERIOD = 60
MEAN_DHT11_TEMPERATURE_HIST_SIZE_MAX = 15

MIN_TEMPERATURE = 32
MIN_MARGIN = 6
MAX_AIR_TEMPERATURE = 40

# GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(WARMER_PIN,GPIO.OUT)
GPIO.output(WARMER_PIN, GPIO.LOW)

# Temp Sensor

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
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c

## Functions
def read_temperature():
    return read_temp()

def read_dht11_temperature():
    return Adafruit_DHT.read_retry(DHT11_VERSION, DHT11_TEMPERATURE_PIN)

def exit_gracefully(signum, frame):
    # In case we get another SIGINT signal during this function
    signal.signal(signal.SIGINT, original_sigint)

    # Turn off the used GPIO pins
    GPIO.output(WARMER_PIN, GPIO.LOW)

    print('\nBye bye :)')
    sys.exit(1)

def toggle_n_times(n):
    heater_on = False
    for _ in range(n):
        heater_on = not heater_on
        if heater_on:
            GPIO.output(WARMER_PIN, GPIO.HIGH)
        else:
            GPIO.output(WARMER_PIN, GPIO.LOW)
        time.sleep(1)

def is_monotonly_decreasing(xs):
    if len(xs) != MEAN_DHT11_TEMPERATURE_HIST_SIZE_MAX:
        return False

    prev = xs[0]
    monotonly_decreasing = True
    for x in xs:
        if x > prev:
           monotonly_decreasing = False
        prev = x
    return monotonly_decreasing

def reboot():
    os.system('sudo reboot')

## Main

# replace SIGINT handler
original_sigint = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, exit_gracefully)
mean_dht11_temperature_hist = []
mean_dht11_temperature_hist_size = 0
prev_heater_on = False

print('DateTime', 'DS18B20-Temperature[C]', 'DHT11-Humidity[%]',
      'Dht11-Temperature[C]', 'HeaterOn', sep=PRINT_SEPARATOR)
while True:

    start_time = time.time()
    # 1: Read Sensor
    temperatures = []
    dht11_humidities = []
    dht11_temperatures = []

    dht11_error = False
    ds18b20_error = False

    for i in range(1,N_MEASUREMENTS+1):
        sys.stdout.flush()
        try:
            temperature = read_temperature()
            temperatures.append(temperature)
        except Exception as e:
            ds18b20_error = True

        try:
            [dht11_humidity, dht11_temperature] = read_dht11_temperature()
            dht11_humidities.append(dht11_humidity)
            dht11_temperatures.append(dht11_temperature)
        except Exception as e:
            dht11_error = True

    if dht11_error or None in dht11_temperatures or None in dht11_humidities:
        print('Connect DHT11 Cables Properly!')
        toggle_n_times(30)
        continue
    elif ds18b20_error or None in temperatures:
        print('Connect DS18B20 Cables Properly!')
        toggle_n_times(30)
        continue

    mean_temperature = np.average(temperatures)
    mean_dht11_humidity = np.average(dht11_humidities)
    mean_dht11_temperature = np.average(dht11_temperatures)

    heater_on = mean_temperature < MIN_TEMPERATURE and mean_dht11_temperature < MAX_AIR_TEMPERATURE;
    if heater_on and prev_heater_on == False:
        mean_dht11_temperature_hist = []
        mean_dht11_temperature_hist_size = 0
    prev_heater_on = heater_on

    # 2: Print Measurement
    print( dt.datetime.now(),
          '{0:0.1f}'.format(mean_temperature),
          '{0:0.1f}'.format(mean_dht11_humidity),
          '{0:0.1f}'.format(mean_dht11_temperature),
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

    if heater_on and is_monotonly_decreasing(mean_dht11_temperature_hist):
        print('Cannot Start Warmer!')
        toggle_n_times(6)
        reboot()

    if len(mean_dht11_temperature_hist) < MEAN_DHT11_TEMPERATURE_HIST_SIZE_MAX:
        mean_dht11_temperature_hist.append(mean_dht11_temperature)
    else:
        mean_dht11_temperature_hist = mean_dht11_temperature_hist[1:] + [mean_dht11_temperature]

