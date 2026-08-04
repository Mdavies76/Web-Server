from socket import *
import os
from datetime import datetime, timezone

SERVER_NAME = "CMPT_371_PROXY"
SERVER_PORT = 80
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.bind(('localhost', SERVER_PORT))
proxySocket.listen(1)
print("Server ready to receive")

while True:
    (clientSocket, addr) = proxySocket.accept()
    request = clientSocket.recv(1024).decode()

    lines = request.split("\r\n")
    requestLine = lines[0].split()
    method = requestLine[0]
    filename = requestLine[1][1:] 
    version = requestLine[2]

    headerFields = {}
    for line in lines[1:]:
        if ": " in line:
            (key, value) = line.split(": ", 1)
            headerFields[key] = value

    body = b""
    timeStamp = ""
    FORBIDDEN = ["secret.html"]

    # cache miss, proxy consults origin server
    if not os.path.exists(filename):
        proxyToServerSocket = socket(AF_INET, SOCK_STREAM)
        proxyToServerSocket.connect(("localhost", 8080))
        proxyToServerSocket.send(request.encode())
        response = proxyToServerSocket.recv(1024)
        # parse response from server to send to client
        lines = response.split("\r\n")
        responseLine = lines[0].split()
        method = responseLine[0]
        filename = responseLine[1][1:] 
        version = responseLine[2]

        headerFields = {}
        for line in lines[1:]:
            if ": " in line:
                (key, value) = line.split(": ", 1)
                headerFields[key] = value

    # send data back to client
    responseCode = "200 OK"
    header = "HTTP/1.1 " + responseCode + "\r\nLast-Modified: " + timeStamp + "\r\nContent-Type: text/html\r\n\r\n"
    if responseCode == "200 OK":
        body = open(filename, 'rb').read()
    clientSocket.send(header.encode())
    clientSocket.send(body)
    clientSocket.close()
    