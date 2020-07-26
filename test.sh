#! /bin/bash
 
# Read Temperature
tempread=`cat /sys/bus/w1/devices/28-*/w1_slave`
# Format
temp=`echo "scale=2; "${tempread##*=}" / 1000" | bc`
 
# Output
echo "The measured temperature is " $temp "°C"
