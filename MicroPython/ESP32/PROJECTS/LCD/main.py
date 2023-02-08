from machine import Pin, SoftI2C
from i2c_lcd import I2cLcd
from time import sleep

i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10_000)     #initializing the I2C method for ESP32
#i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)       #initializing the I2C method for ESP8266

I2C_ADDR = 0x27 # can be checked using i2c.scan()
totalRows = 2
totalColumns = 16

lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)

while True:
    lcd.putstr("I2C LCD Tutorial")
    sleep(2)
    lcd.clear()
    lcd.putstr("Lets Count 0-10!")
    sleep(2)
    lcd.clear()
    for i in range(11):
        lcd.putstr(str(i))
        sleep(1)
        lcd.clear()