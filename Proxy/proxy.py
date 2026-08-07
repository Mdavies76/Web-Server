from socket import *
import os
from datetime import datetime, timezone

PROXY_NAME = "CMPT_371_PROXY"
PROXY_PORT = 80
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.bind(('localhost', PROXY_PORT))
proxySocket.listen(1)
print("Proxy ready to receive")

while True:
    (clientSocket, addr) = proxySocket.accept()
    request = clientSocket.recv(1024).decode()

    print(request)
    # this is what the request looks like, need to parse it into a url to forward
    # curl.exe -x localhost:80 http://localhost:80/test.html 
    """
    GET http://localhost/test.html/ HTTP/1.1
    Host: localhost
    User-Agent: curl/8.21.0
    Accept: */*
    Proxy-Connection: Keep-Alive
    """
    lines = request.split("\r\n")
    requestLine = lines[0].split()
    print("requestLine:", requestLine)
    print("requestLine[1]:", repr(requestLine[1]))
    method = requestLine[0]
    url = requestLine[1].removeprefix("http://")
    print("url: ", repr(url))
    version = requestLine[2]

    headerFields = {}
    for line in lines[1:]:
        if ": " in line:
            (key, value) = line.split(": ", 1)
            headerFields[key] = value

    host_port, path = url.split("/", 1) #host_port = localhost:80, path = test.html
    
    if ":" in host_port: # host_port is localhost:PORTNUM is port is not 80
        host, port = host_port.split(":", 1)
        print("PORT:", repr(port)) 
        port = int(port)
    else:  #if port is 80, its default and therefore doesnt incude it
        host = host_port
        port = 80

    # parse orignal headers into a string
    headersRelay = ""
    for key, value in headerFields.items():
        headersRelay += f"{key}: {value}\r\n"

    # forward the request with original headers
    forwardRequest = f"{method} {path} HTTP/1.1\r\n{headersRelay}\r\n"

    originSocket = socket(AF_INET, SOCK_STREAM)
    print("HOST:", repr(host))
    print("PORT:", repr(port))  
    originSocket.connect((host, port))
    originSocket.send(forwardRequest.encode())