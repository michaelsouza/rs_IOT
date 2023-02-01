import time
import machine
from machine import Pin

ledR = Pin(12, Pin.OUT)
ledG = Pin(13, Pin.OUT)
btnReset = Pin(34, Pin.IN, Pin.PULL_UP)

# set inital state
print('Initializing variables')
ledR.value(1)
ledG.value(1)
time.sleep(1)
ledR.value(0)
ledG.value(0)
time.sleep(0.1)

while True:
    # when button is pressed, its state is false
    btnPressed = not btnReset.value()
    print('btnPressed', btnPressed)
    if btnPressed:        
        # print('btnReset')
        # ledR.value(1)
        # time.sleep(1)
        # ledR.value(0)
        # time.sleep(0.1)
        # machine.reset()
        pass
    time.sleep(0.1)