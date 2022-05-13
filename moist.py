

import numpy as np
import math
import time as t
import matplotlib.pyplot as plt

#Variables
#Humidity
Hum = 0
#Temperature for sensors 1 and 2
T_s1 = 0
T_s2 = 0

#Switches
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

#Main loop
while running:
    #Get the time in hours
    time = t.gmtime()[3]
    #print(time)
    
    #Get the humidity, and temperature data from the sensors
    #TBD
    
    if t_step == steps:
        stop = True
    
    #Set humidity threshold
    Hum_thresh = 0.5
    #If day power, between 7 and 23 use 60% for humidity threshold
    if time < 23 & time > 7:
        Hum_thresh = 0.6
    
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
    
    elif (T_s1 <= 1) or (T_s2 <=1):
        #If temperature falls below 1C turn on heater and turn off dehumidifier
        H = True
        DH = False
        
    #Part where we push the switch signals to the raspberry
    #TBD
    
    #Testing part
    #Temp models
    T_s1 = T_s1 -DH*0.07 + H*0.03
    T_s2 = T_s2 -DH*0.07 + H*0.03
    
    #Hum models
    Hum = Hum - DH*0.01 + 0.001
    
    T_1.append(T_s1)
    T_2.append(T_s2)
    Hums.append(Hum)
    ts.append(t_step)
    switches = np.append(switches, [DH,H])
    
    t_step += 1
            
    if stop:
        running = False
        

        
#Visualization
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
