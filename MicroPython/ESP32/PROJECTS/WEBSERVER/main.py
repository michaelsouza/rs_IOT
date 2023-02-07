import socket
from machine import Pin
from apps import *

am = AppManager()
am.add(AppMain(), True)
am.add(AppWifiScan())

app = AppSwitches()
app.add(12, Pin.LOW, 'LED RED')
app.add(13, Pin.HIGH, 'LED GREEN')

s = socket.socket()
s.bind(('', port))
s.listen(5)

while True:
    conn, addr = s.accept()
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
s.close()
