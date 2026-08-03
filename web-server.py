from socket import *
import os
from datetime import datetime, timezone

SERVER_NAME = "CMPT_371"
SERVER_PORT = 8080
TIME_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', SERVER_PORT))
serverSocket.listen(1)
print("Server ready to receive")

while True:
    (clientSocket, addr) = serverSocket.accept()
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

    if not os.path.exists(filename):
        responseCode = "404 Not Found"
    elif not os.access(filename, os.R_OK): #client doesnt have read access
        responseCode = "403 Forbidden"
    elif version != "HTTP/1.1":
        responseCode = "505 HTTP Version Not Supported"
    else:
        lastModified = datetime.fromtimestamp(os.path.getmtime(filename), timezone.utc)
        timeStamp = lastModified.strftime(TIME_FORMAT)

        if "If-Modified-Since" in headerFields:
            requestTime = datetime.strptime(headerFields["If-Modified-Since"], TIME_FORMAT)
            requestTime = requestTime.replace(tzinfo = timezone.utc)

            if lastModified <= requestTime:
                responseCode = "304 Not Modified"
            else:
                responseCode = "200 OK"
        else:
            responseCode = "200 OK"

        

    header = "HTTP/1.1 " + responseCode + "\r\nLast-Modified: " + timeStamp + "\r\nContent-Type: text/html\r\n\r\n"

    if responseCode == "200 OK":
        body = open(filename, 'rb').read()

    clientSocket.send(header.encode())
    clientSocket.send(body)
    clientSocket.close()