from socket import *
import os

SERVER_NAME = "CMPT_371_PROXY"
SERVER_PORT = 80

proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.bind(('localhost', SERVER_PORT))
proxySocket.listen(1)
print("Proxy ready to receive")

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

    if not os.path.exists(filename): # object stored in proxy
        (proxyToServerSocket, addr) = proxySocket.accept()
        request = clientSocket.recv(1024).decode()
