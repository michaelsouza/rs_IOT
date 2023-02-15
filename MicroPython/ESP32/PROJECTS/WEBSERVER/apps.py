import json
import socket
import network
from time import sleep
from network import WLAN
from i2c_lcd import I2cLcd
from machine import Pin, SoftI2C


def request_value(request: str, field: str) -> str:
    s = next(filter(lambda u: f'{field}=' in u,
             request.split('\n'))).split('&')
    for kv in s:
        k, v = kv.split('=')
        if k == field:
            return v
    return ''


class LCD():
    def __init__(self, I2C_ADDR=0x27, totalRows:int=2, totalColumns:int=16) -> None:            
        # initializing the I2C method for ESP32
        self.i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10_000)
        # i2c = I2C(scl=Pin(5), sda=Pin(4), freq=10000)       #initializing the I2C method for ESP8266

        self.I2C_ADDR = I2C_ADDR  # can be checked using i2c.scan()
        self.totalRows = totalRows
        self.totalColumns = totalColumns

        self.lcd = I2cLcd(self.i2c, I2C_ADDR, self.totalRows, self.totalColumns)
        self.lcd.clear()

    def clear(self):
        self.lcd.clear()

    def print(self, msg: str, clear: bool = False):
        if clear:
            self.clear()
        self.lcd.putstr(msg)

    def println(self, msg: str, clear: bool = False):
        if clear:
            self.clear()
        self.lcd.putstr(f'%-{self.totalColumns}s' % msg)
        

class App(object):
    def __init__(self, name: str, html_path: str):
        self.name = name
        print('Reading', html_path)
        with open(html_path, 'r') as fp:
            self.html = fp.read()
        print('Reading', 'styles.css')
        with open('styles.css', 'r') as fp:
            self.css = fp.read()
        print('Inserting css file into html')
        self.html = self.html.replace(
            '<link rel="stylesheet" href="styles.css">',
            '<style>%s</style>' % self.css
        )

    def get(self, request: str, response: str):
        return self.name, response

    def post(self, request: str):
        pass


class NetManager(object):
    def __init__(self, lcd:LCD) -> None:
        self.lcd = lcd
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.PORT: int = 80

        self.ap = WLAN(network.AP_IF)
        self.connect_ap()

        self.sta = WLAN(network.STA_IF)
        self.connect_sta()
        
    def connect_ap(self):
        self.ap.active(True)
        self.ap.config(essid="ESP32", password="admin")
        for _ in range(10):
            if self.ap.active():
                break
            sleep(1)
        if not self.ap.active():
            self.lcd.println(f'WLAN.AP({self.PORT})', True)
            self.lcd.print('FAILED')
        else:            
            self.socket_bind()

    def connect_sta(self, essid='', password=''):
        with open('profiles.json', 'r') as fp:
            profiles = json.load(fp)
        
        if len(essid) == 0 and len(password) == 0:
            essid = profiles['network']['essid']
            password = profiles['network']['password']
        
        self.sta.connect(essid, password)
        for _ in range(10):
            if self.sta.active():
                break
            sleep(1)
        if not self.sta.active():
            self.lcd.println(f'WLAN.STA({self.PORT})', True)
            self.lcd.print('FAILED')
        else:
            self.IP = self.sta.ifconfig()[0]
            self.lcd.print(self.IP)
            # save valid essid, password
            profiles['network']['essid'] = essid
            profiles['network']['password'] = password
            with open('profiles.json', 'w') as fp:
                json.dump(profiles, fp)
            self.socket_bind()            

    def socket_bind(self):
        if self.sta.active():
            wlan = self.sta
        else:
            wlan = self.ap
        self.socket.bind((wlan.ifconfig()[0], self.PORT))
        self.socket.listen(5)
        self.lcd_status()

    def lcd_status(self) -> None:
        if self.sta.active():
            wlan = self.sta
            self.lcd.println(f'WLAN.STA({self.PORT})', True)            
        else:
            wlan = self.ap
            self.lcd.println(f'WLAN.AP({self.PORT})', True)
        self.lcd.print(wlan.ifconfig()[0])


class AppManager(object):
    def __init__(self, lcd:LCD):
        self.apps = {}
        self.app_name = ''
        self.lcd = lcd
        self.nm = NetManager(lcd)

    def add(self, app: App, default: bool = False):
        self.apps[app.name] = app
        if default:
            self.app_name = app.name

    def get(self, request: str):
        response = "HTTP/1.1 200 OK\n\n"
        self.app_name, response = self.apps[self.app_name].get(
            request, response)
        return response

    def post(self, request: str):
        self.app_name = self.apps[self.app_name].post(request)


class AppMain(App):
    def __init__(self, nw: NetManager):
        super().__init__(name='main', html_path='web-main.html')
        self.nw = nw

    def get(self, request: str, response: str):
        response += self.html
        if self.nw.sta.active():
            response = response.replace('<p>@ESP32</p>','<p>@ESP32 (CONNECTED)</p>')
        return self.name, response + self.html

    def post(self, request: str):
        app_name = request_value(request, 'app_name')
        return app_name


class AppWifiScan(App):
    def __init__(self, nw:NetManager, lcd:LCD):
        super().__init__(name='wifiscan',  html_path='web-wifiscan.html')
        self.lcd = lcd        
        self.nw = nw
        self.SSID = {}

    def scan(self):
        self.lcd.println('SCAN NETWORKS', True)
        self.SSID = {}
        for ssid in sorted(self.nw.sta.scan()):
            self.SSID[ssid[0].decode()] = ssid
        self.lcd.println(f'FOUND {len(self.SSID)}')
        return self.SSID

    def get(self, request: str, response: str):
        self.scan()
        s = """
            <li>
                <input type="radio" id="ssid-yyy" name="ssid" value="xxx">
                <label for="nw-yyy">xxx</label><br>
            </li>
        """
        m = ''
        for k, ssid in enumerate(sorted(self.SSID)):
            m += s.replace('xxx', ssid).replace('yyy', str(k))
        response += self.html.replace('<span></span>', m)
        if self.nw.sta.active():
            response = response.replace('<p>@ESP32</p>','<p>@ESP32 (CONNECTED)</p>')
        return self.name, response

    def post(self, request: str):
        essid = request_value(request, 'essid')
        password = request_value(request, 'password')
        app_name = request_value(request, 'app_name')
        self.nw.connect_sta(essid=essid, password=password)
        return app_name


class AppSwitches(App):
    def __init__(self, nw:NetManager):
        super().__init__(name='switches',  html_path='web-switches.html')
        self.nw = nw
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
        if self.nw.sta.active():
            response = response.replace('<p>@ESP32</p>','<p>@ESP32 (CONNECTED)</p>')
        return self.name, response

    def post(self, request: str):
        app_name = request_value(request, 'app_name')
        if app_name == self.name:
            for id in self.switches:
                data = self.switches[id]
                data['value'] = request_value(request, f'sw-{id}') == '1'
            self.update()
        return app_name


if __name__ == "__main__":
    led12 = Pin(12, Pin.OUT)
    led13 = Pin(13, Pin.OUT)
    led12.value(1)
    led13.value(1)
    lcd = LCD()
    nw = NetManager(lcd=lcd)
    am = AppManager(lcd=lcd)
    app = AppWifiScan(nw=nw, lcd=lcd)
    am.add(app, default=True)
    
    while True:
        conn, addr = nw.socket.accept()
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
        nw.lcd_status()
