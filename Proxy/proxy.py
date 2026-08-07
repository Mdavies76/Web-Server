from socket import *
import os
from datetime import datetime, timezone

SERVER_NAME = "CMPT_371_PROXY"
SERVER_PORT = 8888 # changed to 8888 because on mac it requires admin/root stuff
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

proxySocket = socket(AF_INET, SOCK_STREAM)
proxySocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
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

    # cache miss
    if not os.path.exists(filename):
        print("Cache Miss")
        proxyToServerSocket = socket(AF_INET, SOCK_STREAM)
        proxyToServerSocket.connect(("localhost", 8080))
        proxyToServerSocket.send(request.encode())
        response = proxyToServerSocket.recv(1024)
        proxyToServerSocket.close()
        # parse response from server to send to client
        responseText = response.decode()
        lines = responseText.split("\r\n")
        
        for i in range(len(lines)): # loop to find where the headers end and the html body starts 
            if lines[i] == "":
                body = "\r\n".join(lines[i+1:]).encode()
                if "200" in lines[0]:
                    open(filename, "wb").write(body)
                break
        clientSocket.send(response)
        clientSocket.close()
    else:
    # send data back to client
        print("Cache Hit")
        responseCode = "200 OK"
        body = open(filename, 'rb').read()
        header = "HTTP/1.1 " + responseCode + "\r\nLast-Modified: " + timeStamp + "\r\nContent-Type: text/html\r\n\r\n"
        if responseCode == "200 OK":
            body = open(filename, 'rb').read()
        clientSocket.send(header.encode())
        clientSocket.send(body)
        clientSocket.close()
