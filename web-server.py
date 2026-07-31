from socket import *
serverName = "CMT_371"
serverPort = 8080
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(1)
print("Server ready to receive")
while True:
    (clientSocket, addr) = serverSocket.accept()
    request = clientSocket.recv(1024).decode()
    filename = request.split()[1]
    body = open(filename[1:], 'rb').read()
    clientSocket.send(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    clientSocket.send(body)
    clientSocket.close()