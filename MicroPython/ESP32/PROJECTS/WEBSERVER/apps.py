import json
import network
from time import sleep
from machine import Pin, SoftI2C
from i2c_lcd import I2cLcd

def LCD():
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10_000)     #initializing the I2C method for ESP32
    #i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)       #initializing the I2C method for ESP8266

    I2C_ADDR = 0x27 # can be checked using i2c.scan()
    totalRows = 2
    totalColumns = 16

    lcd = I2cLcd(i2c, I2C_ADDR, totalRows, totalColumns)
    lcd.clear()
    return lcd

def get_value(request: str, field: str) -> str:
    s = next(filter(lambda u: f'{field}=' in u,
             request.split('\n'))).split('&')
    for kv in s:
        k, v = kv.split('=')
        if k == field:
            return v
    return ''


class App(object):
    def __init__(self, name:str, html_path:str):
        self.name = name
        print('Reading', html_path)
        with open(html_path, 'r') as fp:
            self.html = fp.read()
        print('Reading', 'style.css')
        with open('style.css', 'r') as fp:
            self.css = fp.read()
        print('Inserting css file into html')
        self.html = self.html.replace(
            '<link rel="stylesheet" href="style.css">',
            '<style>%s</style>' % self.css
        )

    def get(self, request: str, response: str):
        return self.name, response

    def post(self, request: str):
        pass    


class AppManager(object):
    def __init__(self):
        self.apps = {}
        self.app_name = ''

    def add(self, app: App, default: bool = False):
        self.apps[app.name] = app
        if default:
            self.app_name = app.name

    def get(self, request: str):
        response = "HTTP/1.1 200 OK\n\n"
        self.app_name, response = self.apps[self.app_name].get(request, response)
        return response

    def post(self, request: str):
        self.app_name = self.apps[self.app_name].post(request)


class AppMain(App):
    def __init__(self):
        super().__init__(name='main', html_path='web-main.html')

    def get(self, request: str, response: str):
        return self.name, response + self.html

    def post(self, request: str):
        app_name = get_value(request, 'app_name')
        return app_name


class AppWifiScan(App):
    def __init__(self, lcd):
        super().__init__(name='wifiscan',  html_path='web-wifiscan.html')
        self.lcd = lcd
        self.ssid, self.password = self.login_load()
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(True)
        self.SSID = self.scan() # set of available ssid's
        self.connect()

    def connect(self):        
        self.lcd.putstr('CONNECT STA_IF', True)
        if self.ssid in self.SSID:
            self.sta_if.connect(self.ssid, self.password)
            sleep(0.5)        
        if self.isconnected():
            IP = self.sta_if.ifconfig()[0]
            self.lcd.putstr('%-16s' % 'STA_IF:IP', True)
            self.lcd.putstr(f'{IP}')        
        else:
            self.lcd.putstr('FAILED')
            

    def isconnected(self):
        return self.sta_if.isconnected()

    def login_load(self):
        with open('profiles.json', 'r') as fp:
            self.profiles = json.load(fp)

        ssid = self.profiles['network']['ssid']
        password = self.profiles['network']['password']        
        return ssid, password

    def login_save(self, ssid:str, password:str):
        with open('profiles.json', 'r') as fp:
            self.profiles = json.load(fp)

        self.profiles['network']['ssid'] = ssid
        self.profiles['network']['password'] = password
        with open('profiles.json', 'w') as fp:
            json.dump(self.profiles, fp)

    def scan(self):
        self.lcd.putstr('SCAN NETWORKS', True)
        SSID = {}
        for ssid in sorted(self.sta_if.scan()):
            SSID[ssid[0].decode()] = ssid
        self.lcd.putstr(f'FOUND {len(SSID)}')
        return SSID

    def get(self, request: str, response: str):
        s = """
            <input type="radio" id="ssid-yyy" name="ssid" value="xxx" class="m-top-5" zzz>
            <label for="nw-yyy">xxx</label><br>
        """
        m = ''
        for k, ssid in enumerate(self.networks):
            m += s.replace('xxx', ssid) \
                .replace('yyy', str(k)) \
                .replace('zzz', 'checked' if ssid == self.ssid and self.isconnected() else '')
        response += self.html.replace('<span></span>', m)
        return self.name, response

    def post(self, request: str):
        self.ssid = get_value(request, 'ssid')
        self.password = get_value(request, 'password')
        self.connect()
        if self.isconnected():
            self.login_save(self.ssid, self.password)
            app_name = get_value(request, 'main')
        else:
            app_name = self.name
        return app_name


class AppSwitches(App):
    def __init__(self):
        super().__init__(name='switches',  html_path='web-switches.html')
        # read initial states from machine
        self.switches = {}

    def add(self, id: int, initval: bool, label: str):
        pin = Pin(id, Pin.OUT)
        pin.value(initval)
        data = {
            'pin': pin,
            'label': label,
            'value': initval,
        }
        self.switches[id] = data
        self.update()

    def update(self):
        for id in self.switches:
            data = self.switches[id]
            pin, value = data['pin'], data['value']
            pin.value(value)

    def get(self, request: str, response: str):
        s = """
            <div class="switch-div">
                <div class="switch-label">
                    <h3>xxx</h3>
                </div>
                <div class="switch-item">
                    <label class="switch">
                        <input type="checkbox" id="zzz" yyy>
                        <span class="slider round"></span>
                    </label>
                </div>
            </div>
        """
        m = ''
        for id in self.switches:            
            label = self.switches[id]['label']
            value = self.switches[id]['value']
            m += s.replace('xxx', label) \
                .replace('yyy', 'checked' if value else '') \
                .replace('zzz', f'sw-{id}')
        response += self.html.replace('<span></span>', m)
        return self.name, response

    def post(self, request: str):
        app_name = get_value(request, 'app_name')
        if app_name == self.name:
            for id in self.switches:
                data = self.switches[id]
                data['value'] = get_value(request, f'sw-{id}') == '1'
            self.update()
        return app_name


if __name__ == "__main__":
    lcd = LCD()
    app = AppWifiScan(lcd)