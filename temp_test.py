#!/usr/bin/env python3


import board
import adafruit_dht

dhtdevice = adafruit_dht.DHT22(board.D4)

humidity, temperature = dhtdevice.humidity, dhtdevice.temperature

humidity = round(humidity, 2)
temperature = round(temperature, 2)

if humidity is not None and temperature is not None:

  print ('Temperatuur: {0:0.1f}*C'.format(temperature))
  print ('Luchtvochtigheid: {0:0.1f}%'.format(humidity))

else:

  print ('Geen data ontvangen')