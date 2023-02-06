# https://realpython.com/python-sockets/
# https://emalsha.wordpress.com/2016/11/22/how-create-http-server-using-python-socket/
# https://stackoverflow.com/questions/21153262/sending-html-through-python-socket-server
# https://stackoverflow.com/questions/4741243/how-to-pick-just-one-item-from-a-generator

import socket
from apps import *

am = AppManager()
am.add(AppMain(), True)
am.add(AppSwitches())
am.add(AppWifiScan())

s = socket.socket()
host, port = '127.0.0.1', 8000
s.bind((host, port))
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
