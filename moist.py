

import numpy as np
import math
import os
import glob
import time as t
#import matplotlib.pyplot as plt
import Adafruit_DHT
#from gpiozero import OutputDevice
import RPi.GPIO as GPIO


#Setup GPIO devices
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Set list of output GPIO pins
#Pin 22 corresponds to heater and Pin 23 corresponds to dehumidifier
OutputPins = [23, 24]

#Loop through devices and turn to off
for i in OutputPins:
    GPIO.setup(i, GPIO.OUT)
    GPIO.output(i, False)


#Variables
wait = 1
#Humidity
Hum = 0
#Temperature for sensors 1 and 2
T_s1 = 0
T_s2 = 0

#Relays
#heater = OutputDevice(1)
#dehumidifier = OutputDevice(2)

#Switches
#Dehumidifier switch
DH = False
#Heater switch
H = False
#Stop switch for detecting if stop signal was given
stop = False
#Running switch
running = True
vis = False


#Testing
steps = 10000
t_step = 0
Hum = 0.7
T_s1 = 7
T_s2 = 7
T_1 = []
T_2 = []
Hums = []
ts = []
switches = np.array([])

#Stuff for reading temp_sensor
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

#Reading temp sensor
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        t.sleep(wait)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def read_hum():
    t.sleep(wait)
    hum, temp  = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 17) #was 4
    #Divide by 100 to get as decimal
    hum = hum/100
    return(hum,temp)
    

#Main loop
while running:
    #Get the time in hours
    #time = t.gmtime()[3]
    #print(time)
    
    #Get the humidity, and temperature data from the sensors
    Hum, T_s1 = read_hum()
    T_s2 = read_temp()
    
   
    #Set humidity threshold
    Hum_thresh = 0.5
    #If day power, between 7 and 23 use 60% for humidity threshold
    #if time < 23 & time > 7:
     #   Hum_thresh = 0.6
    
    DH = False
    H = False
    if Hum >= Hum_thresh:
        
        #Turn on dehumidifier
        DH = True
        
        #Check if heater is on and if dehumidifier is not frozen
        if H:
            if (T_s1 >= 5) & (T_s2 >= 5):
                #If true turn heater off
                H = False
    
    elif (T_s1 <= 1) or (T_s2 <= 1):
        #If temperature falls below 1C turn on heater and turn off dehumidifier
        H = True
        DH = False
        
    #Part where we push the switch signals to the raspberry
    if H:
        #heater.on()
        GPIO.output(OutputPins[0],True)
    else:
        GPIO.output(OutputPins[0],False)
        #heater.off()
        
    if DH:
        GPIO.output(OutputPins[1],True)
        #dehumidifier.on()    
    else:
        GPIO.output(OutputPins[1],False)
        #dehumidifier.off()
    
    #Print for testing
    print ('Temperatuur sensor 1:', T_s1)
    print ('Temperatuur sensor 2:',T_s2)
    print ('Luchtvochtigheid:', Hum)
    print ('Heater:', H)
    print ('Ontvochtiger:', DH)
    
    #Testing part
    if vis:
         
        T_1.append(T_s1)
        T_2.append(T_s2)
        Hums.append(Hum)
        ts.append(t_step)
        switches = np.append(switches, [DH,H])
        
        t_step += 1
            
    if stop:
        running = False
        

"""        
#Visualization
if vis:
    plt.title("Temperature sensor 1 and 2")
    plt.plot(ts, T_1, label = "sensor1")
    plt.plot(ts, T_2, label = "sensor2")
    plt.legend()
    plt.show()
    
    plt.title("Humidity level")
    plt.plot(ts,Hums)
    plt.show()
    
    switches = np.reshape(switches, (steps+1,2))
    
    plt.scatter(ts,switches[:,0],s =0.001)
    plt.show()
 """       