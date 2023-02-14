import socket
import network
from time import sleep
from machine import Pin, SoftI2C, soft_reset
from apps import *

# blink just to say hello
ledR = Pin(12, Pin.OUT)
ledG = Pin(13, Pin.OUT)
for _ in range(3):
    ledR.value(1)
    ledG.value(1)
    sleep(1)
    ledR.value(0)
    ledG.value(0)
    sleep(0.5)

lcd = LCD()

lcd.putstr('ADD APPS', True)
am = AppManager()
am.add(AppMain(), True)       # add AppMain
am.add(AppWifiScan(lcd))      # add AppWifiScan
app = AppSwitches()
app.add(12, True, 'PIN 12')   # add Pin.OUT
app.add(13, True, 'PIN 13')   # add Pin.OUT
am.add(app)                   # add AppSwitches
lcd.putstr('WLAN.AP_IF', True)
sta_ap = network.WLAN(network.AP_IF)
sta_ap.active(True)
sta_ap.config(essid="ESP32", password="123456789")

while sta_ap.active() == False:
    pass

HOST = sta_ap.ifconfig()[0]
PORT = 80

lcd.putstr('SOCKET.AF_INET')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

lcd.putstr('%-16s' % 'AP_IF:PORT', True)
lcd.putstr(f'{HOST}:{PORT}')
sleep(0.5)

while True:
    conn, addr = s.accept()
    request = conn.recv(1024).decode()
    
    print(request)
    if "GET / " in request:
        response = am.get(request)
        conn.send(response.encode())

    elif "POST /submit-form" in request:
        am.post(request)
        conn.send("HTTP/1.1 200 OK\n\n".encode())
    
    else:
        conn.send("HTTP/1.1 404 Not Found\n\n".encode())
    
    conn.close()
    lcd.putstr('%-16s' % 'AP_IF:PORT', True)
    lcd.putstr(f'{HOST}:{PORT}')
