try:
    import usocket as socket
except:
    import socket

import network

import esp
esp.osdebug(None)

import gc
gc.collect()


def web_page(nws: dict):
    """Create web_page"""
    html = """  <html>
                    <head>
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                    </head>
                    <body>
                        %s
                    </body>
                </html>"""

    html_body = ""
    for nw_key in nws:
        print('nw_key', nw_key)
        nw_name = nws[nw_key]
        print('nw_name', nw_name)
        html_body += f"<p>{str(nw_key)}. {nw_name}</p>\n"
    return html % html_body

print('SCANNING NETWORKS')
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

print('AVAILABLE NETWORKS')
available_networks = {}
for k, nw in enumerate(sorted(sta_if.scan())):
    available_networks[k] = str(nw[0])[2:-1]
    print(f'\t{k+1}. {available_networks[k]}')

print('CREATING AP ...')
sta_ap = network.WLAN(network.AP_IF)
sta_ap.active(True)
sta_ap.config(essid="MicroPython AP", password="123456789")

while sta_ap.active() == False:
    pass

print('AP CREATED')
print(sta_ap.ifconfig())

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',80))
s.listen(5)

while True:
    conn, addr = s.accept()
    print(f'CONNECTION FROM {str(addr)}')
    request = conn.recv(1024)
    print(f'CONTENT: {str(request)}')
    response = web_page(available_networks)
    conn.send(response)
    conn.close()