from machine import Pin

def get_value(request: str, field: str) -> dict:
    s = next(filter(lambda u: f'{field}=' in u,
             request.split('\n'))).split('&')
    for kv in s:
        k, v = kv.split('=')
        if k == field:
            return v
    return None


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

        with open('web-' + self.app_name + '.html', 'r') as fp:
            response += fp.read()

        self.app_name, response = self.apps[self.app_name].get(
            request, response)

        return response

    def post(self, request: str):
        self.app_name = self.apps[self.app_name].post(request)


class AppMain(App):
    def __init__(self):
        self.name = 'main'

    def get(self, request: str, response: str):
        return self.name, response

    def post(self, request: str):
        app_name = get_value(request, 'app_name')
        return app_name


class AppWifiScan(App):
    name = 'wifiscan'

    def __init__(self):
        self.fav_network = None
        self.password = None

    @property
    def networks(self):
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        nws = []
        for nw in enumerate(sorted(sta_if.scan())):
            nws.append(nw[0].decode())
        return nws

    def get(self, request: str, response: str):
        s = """
            <input type="radio" id="nw-YYY" name="fav_network" value="XXX">
            <label for="nw-YYY">XXX</label><br>
        """
        self.scan()
        m = ''
        for k, nw in enumerate(self.networks):
            m += s.replace('XXX', nw).replace('YYY', str(k))
        return self.name, response.replace('<items>', m)

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

    def add(self, id:int, state:bool, label:str):
        pin = Pin(id, Pin.OUT)
        data = {
            'pin':pin,
            'label': label, 
            'state': False,
        }
        self.switches[f'sw-{id}'] = data

        self.update()

    def update(self):
        for id in self.switches:
            data = self.switches[f'{id}']
            pin, state = data['pin'], data['state'] 
            if state:
                pin.high()
            else:
                pin.low()
        
    def get(self, request: str, response: str):
        s = """
            <div class="grid-item">
                <h3>XXX</h3>
            </div>
            <div class="grid-item vertical-center">
                <label class="switch">
                    <input type="checkbox" name="switch" id="ZZZ" YYY>
                <span class="slider round"></span>
                </label>
            </div>
            """
        m = ''
        for id in self.switches:
            label = self.switches[id]['label']
            state = self.switches[id]['state']
            m += s.replace('XXX', label) \
                .replace('YYY', 'checked' if state else '') \
                .replace('ZZZ', id)
        response = response.replace('<items>', m)
        return self.name, response

    def post(self, request: str):
        app_name = get_value(request, 'app_name')
        if app_name == self.name:
            for id in self.switches:
                data = self.switches[id]
                data['state'] = bool(get_value(request, str(id)))
            self.update()
        return app_name
