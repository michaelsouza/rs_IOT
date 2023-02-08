import time
import machine

ledR = machine.Pin(12, machine.Pin.OUT)
ledG = machine.Pin(13, machine.Pin.OUT)
while True:
    ledG.value(1)
    ledR.value(1)
    time.sleep(0.2)
    ledG.value(0)
    ledR.value(0)
    time.sleep(0.2)
