#!/usr/bin/env python

import os
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


#read GPIO data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ( (adcnum > 7) or (adcnum < 0) ):
                return -1
				
        GPIO.output(cspin, True)	#set CS high
        GPIO.output(clockpin, False)	#start clock low
        GPIO.output(cspin, False)	#bring CS low
 
        commandout = adcnum
        commandout |= 0x18	#start bit + single-ended bit
        commandout <<= 3	#we only need to send 3 bits here
        
	for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                #negative clock signals generator
		commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
		#read in one empty bit, one null bit and 10 ADC bits
        adcout = 0
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1	#shift bit to left
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
        adcout >>= 1	#first bit is 'null' so drop it
        time.sleep(1)
        return adcout
 
#pins connected from the GPIO port on the ADC to the Raspberry Pi
CLK = 18
MISO = 23
MOSI = 24
CS = 25
 
# set up the GPIO interface pins
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)
 
#water flow sensor connected to adc #0
flow_adc = 0
count = 0
value = 0
while True:
        #read the analog pin
        value = readadc(flow_adc, CLK, MOSI, MISO, CS)
	val = value	
	while value < 512:
		value = readadc(flow_adc, CLK, MOSI, MISO, CS)
		count = count + 1
		print(val)
		print(count)
		flow = count / 5.5
		print(flow)
#	while (value < 512):
#		value = readadc(flow_adc, CLK, MOSI, MISO, CS)
			
#	print(count);
		
