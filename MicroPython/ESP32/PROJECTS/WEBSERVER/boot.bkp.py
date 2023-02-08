try:
    import usocket as socket
except:
    import socket

import machine
import network
import esp
import gc
from time import sleep

esp.osdebug(None)
gc.collect()

def webpage_builder(html_body):
    """Create web_page"""
    html = """  
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1">
            </head>
            <body>
                %s
            </body>
            </html>
    """
    return bytes(html % html_body, 'utf-8')


def webpage_select_network(avns):
    html = """
        <h1>Select the network</h1>
        <form action=".">
    """
    for k, nw_name in enumerate(avns):                
        html += f'<input type="radio" id="net-{k}" name="net-name" value="{nw_name}">'                
        html += f'<label for="NETWORK_{k}">{nw_name}</label><br>'
    
    html += """
        <label for="net-pass">Password (8 characters minimum):</label>
        <input type="password" id="id-pass" name="net-pass">
        <input type="submit" value="Sign in">
        </form>
    """
    
    return webpage_builder(html)
    
print('SEARCHING NETWORKS')
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

avns = [nw[0].decode('utf-8') for nw in sorted(sta_if.scan())]
if len(avns) > 0:
    print('AVAILABLE NETWORKS')
    for nw in avns:
        print('\t', nw)


print('CREATING ACCESS POINT')
sta_ap = network.WLAN(network.AP_IF)
sta_ap.active(True)
sta_ap.config(essid="MicroPython AP", password="123456789")

while sta_ap.active() == False:
    pass

print('ACCESS POINT CONFIGS')
print(sta_ap.ifconfig())

# https://www.internalpointers.com/post/making-http-requests-sockets-python
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(('',80))
soc.listen(5)

ledR = machine.Pin(12, machine.Pin.OUT)
while True:
    ledR.value(1)
    con, add = soc.accept()
    req_bin = con.recv(1024)
    req_str = req_bin.decode()
    
    print(req_str)
    for s in req_str.split('\r\n'):
        if 'net-name' in s and 'net-pass' in s:
            print(s)
            con.send(webpage_builder("s"))
    
    con.send(webpage_select_network(avns))
    con.close()
    ledR.value(0)
    sleep(1)
