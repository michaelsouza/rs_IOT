import esp

esp.osdebug(None)

from machine import Pin, SoftI2C

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10_000)
devs = i2c.scan()

for dev in devs:
    print('dev_addr:', hex(dev))