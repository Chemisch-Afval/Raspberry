
import numpy as np

import os
import glob
import time as t

#Packages for visualization
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
from datetime import datetime

#packages for reading sensor data
import Adafruit_DHT
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
#Error counter
err_count = [0,0]
#Set freeze threshold
freeze_thresh = 2
#Set unfreeze threshold
unfreeze_thresh = 4
#Set humidity threshold
Hum_thresh = 0.55
#Delay after taking measurments
wait = 1
#Humidity
Hum = 0
#Temperature for sensors 1 and 2
T_s1 = 0
T_s2 = 0


#Switches
#save data
save = True
#Visualization
vis = True
#Dehumidifier switch
DH = False
#Heater switch
H = False
#Stop switch for detecting if stop signal was given
stop = False
#Running switch
running = True


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

#File name for writing sensor data
data_file = "data.txt"
#File_limit
file_limit = 100

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


def animate(data):
    timeC = []
    timeC = np.array([str(data[:,-3] + ":" + str(data[:,-2]) + ":" + str(data[:,-1]))])
    
    """
    for rows in data.shape[0]:
        time = rows[0]
            #print timeA
        time_string = datetime.strptime(time,'%H:%M:%S')
        #print(time_string)
        try:
            timeC.append(time_string)
        except:
            print("dont know")
    """
        
    #Create axes for plotting, one for humidity, one for temperature, and two for both switches
    fig, ax = plt.subplots(2, 2, sharex= True)
    ax[0,0].title("Humidity")
    ax[0,1].title("Temperature")
    ax[1,0].title("Dehumidifier state")
    ax[1,1].title("Heater state")

    ax[0,0].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    #Plot humidity
    ax[0,0].plot(timeC,data[:,1], 'c', linewidth = 3.3)
    #Plot temperatures
    ax[0,1].plot(timeC,data[:,2], 'c', linewidth = 3.3)
    ax[0,1].plot(timeC,data[:,3], 'c', linewidth = 3.3)
    #Plot dehumidifier state
    ax[1,0].plot(timeC,data[:,4], 'c', linewidth = 3.3)
    #Plot heater state
    ax[1,1].plot(timeC,data[:,5], 'c', linewidth = 3.3)
    plt.title('Data')
    plt.xlabel('Time')
    
    

#Main loop
while running:
    #Get the time in hours
    #time = t.gmtime()[3]
    #print(time)
    
    #Get the humidity, and temperature data from the sensors
    try:
        Hum, T_s1 = read_hum()
        #Store values for handling sensor errors
        Hum_stored, T_s1_stored = Hum, T_s1
        err_count[0] = 0
    except:
        print("Could not read humidity sensor, using previous measurments")
        err_count[0] += 1
        Hum, T_s1 = Hum_stored, T_s1_stored
        if err_count[0] >= 5:
            print("Could not read humidity sensor 5 consecutive times. Check wiring")
        
    try:
        T_s2 = read_temp()
        T_s2_stored = T_s2
        err_count[1] = 0
    except:
        print("Could not read temperature sensor, using previous measurement")
        err_count[1] += 1
        T_s2 = T_s2_stored
        if err_count[1] >= 5:
            print("Could not read temperature sensor 5 consecutive times. Check wiring")
   

    #If day power, between 7 and 23 use 60% for humidity threshold
    #if time < 23 & time > 7:
     #   Hum_thresh = 0.6
    
    DH = False
    #H = False
    
    #Turn on dehumidifier if threshold has been reached
    if Hum >= Hum_thresh:
        DH = True
        Hum_thresh = 0.5
        
    elif Hum <= 0.5:
        Hum_thresh = 0.55
        
    #Check if heater is on and if dehumidifier is not frozen
    if H:
        if (T_s1 >= unfreeze_thresh) & (T_s2 >= unfreeze_thresh):
            #If true turn heater off
            H = False
               
    #Check if heater is frozen
    if (T_s1 <= freeze_thresh) or (T_s2 <= freeze_thresh):
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
        
    if save:
        #Data is ordered: 
        #timestamp, humidity, temperature of humidity sensor, temperature sensor, dehumidifier state, and heater state
        hour = t.gmtime()[3]
        minute = t.gmtime()[4]
        second = t.gmtime()[5]
        data = [Hum, T_s1, T_s2, DH, H, hour, minute, second]
        
        try:
            data_from_file = np.loadtxt(data_file, delimiter = ",")
            data_from_file = np.append(data_from_file,data)
            #Keep only up to 100 measurements, thus cut off the first measurement when length exceeds limit
            if data_from_file.shape[0] > file_limit:
                data_from_file = data_from_file[1:,:]
        except:
            print("No data written to file yet will write new data")
            data_from_file = data
        
        #Save the data back to the data file
        np.savetxt(data_file, data_from_file, delimiter = ",")
        
        
        #Display results in dynamic graph
        if vis:
            fig = plt.figure()
            rect = fig.patch
            rect.set_facecolor('#0079E7')
    
            ani = animation.FuncAnimation(fig, animate(data_from_file), interval = 6000)   
            plt.show()


    

    #Print for testing
    print ('Temperatuur sensor 1:', T_s1)
    print ('Temperatuur sensor 2:',T_s2)
    print ('Luchtvochtigheid:', Hum)
    print ('Heater:', H)
    print ('Ontvochtiger:', DH)
    
            
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