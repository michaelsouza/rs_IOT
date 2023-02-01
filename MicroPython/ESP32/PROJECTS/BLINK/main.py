import time
import machine

ledG = machine.Pin(13, machine.Pin.OUT)
while True:
    ledG.value(1)
    time.sleep(1)
    ledG.value(0)
    time.sleep(1)
