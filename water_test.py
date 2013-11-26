#!/usr/bin/env python

import sqlite3
import os
import time
import glob
import RPi.GPIO as GPIO
 
#global variables
speriod=(15*60)-1
dbname='/home/pi/1-1/mydatabase.db'

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
 
while True:
        #read the analog pin
        value = readadc(flow_adc, CLK, MOSI, MISO, CS)
        tmp1 = ' Value : ' + repr(value) + ' Hz '
		
		#change value to volt
        volts = (value * 5.0 / 1023)
		tmp2 = ' Volt : ' + repr(volts) + ' V '
        
		#change volt to flow L/min 
		flowL = ' flow : ' +repr(volts / 5.5) + ' L/min '
 
		#change flow L/min to m^3/hr
		FLOW = ' FLOW : ' +repr(volts / (5.5 * 16.667) + ' m^3/hr '
		
		
		water_flow = FLOW
		if water_flow != None:
			print "water flow="+str(water_flow)
		else:
        # Sometimes reads fail on the first attempt
        # so we need to retry
			water_flow = FLOW
			print "water flow="+str(water_flow)

        #Store the flow in the database
		log_flow(flow)

		#display the contents of the database
		display_data()
		
		
        #hang out and do nothing for a second
        time.sleep(1)




#store the flow in the database
def log_flow(flow):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("INSERT INTO waters values(datetime('now'), (?))", (flow,))

    conn.commit()	#commit the changes

    conn.close()


#display the contents of the database
def display_data():

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM waters"):
        print row

    conn.close()


