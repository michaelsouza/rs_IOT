from machine import Pin
import network


def get_value(request: str, field: str) -> str:
    s = next(filter(lambda u: f'{field}=' in u,
             request.split('\n'))).split('&')
    for kv in s:
        k, v = kv.split('=')
        if k == field:
            return v
    return ''


class App(object):
    def __init__(self):
        self.name = ''

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
        self.name = 'main'
        with open('web-main.html', 'r') as fp:
            self.html = fp.read()

    def get(self, request: str, response: str):
        return self.name, response + self.html

    def post(self, request: str):
        app_name = get_value(request, 'app_name')
        return app_name


class AppWifiScan(App):
    name = 'wifiscan'

    def __init__(self):
        self.fav_network = None
        self.password = None
        with open('web-wifiscan.html', 'r') as fp:
            self.html = fp.read()

    @property
    def networks(self):
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        nws = []
        for nw in enumerate(sorted(sta_if.scan())):
            nws.append(str(nw[1][0]))
        return nws

    def get(self, request: str, response: str):
        s = """
            <input type="radio" id="nw-YYY" name="fav_network" value="XXX">
            <label for="nw-YYY">XXX</label><br>
        """
        m = ''
        for k, nw in enumerate(self.networks):
            m += s.replace('XXX', nw).replace('YYY', str(k))
        response += self.html.replace('<items></items>', m)
        return self.name, response

    def post(self, request: str):
        self.fav_network = get_value(request, 'fav_network')
        self.password = get_value(request, 'password')
        app_name = get_value(request, 'app_name')
        return app_name


class AppSwitches(App):
    def __init__(self):
        self.name = 'switches'
        # read initial states from machine
        self.switches = {}
        with open('web-switches.html', 'r') as fp:
            self.html = fp.read()

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
            <input type="checkbox" id="ZZZ" name="switch" YYY>
            <label for="ZZZ">XXX</label><br>
            """
        m = ''
        for id in self.switches:            
            label = self.switches[id]['label']
            value = self.switches[id]['value']
            m += s.replace('XXX', label) \
                .replace('YYY', 'checked' if value else '') \
                .replace('ZZZ', f'sw-{id}')
        response += self.html.replace('<items></items>', m)
        return self.name, response

    def post(self, request: str):
        app_name = get_value(request, 'app_name')
        if app_name == self.name:
            for id in self.switches:
                data = self.switches[id]
                data['value'] = get_value(request, f'sw-{id}') == '1'
            self.update()
        return app_name
