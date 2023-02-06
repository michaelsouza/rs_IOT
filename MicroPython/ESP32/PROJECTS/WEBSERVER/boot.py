try:
    import usocket as socket
except:
    import socket

import network

import esp
esp.osdebug(None)

import gc
gc.collect()

print('CREATING AP')
sta_ap = network.WLAN(network.AP_IF)
sta_ap.active(True)
sta_ap.config(essid="MicroPython AP", password="123456789")

while sta_ap.active() == False:
    pass

print('AP CREATED')
print(sta_ap.ifconfig())
