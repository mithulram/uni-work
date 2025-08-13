import socket
import time
import os

PORT=4450

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', PORT))
hostname=socket.gethostname()
while True:
	print("Waiting for request...")
	message, address = server_socket.recvfrom(1024)
	print("Request received...")
	message = message.decode('utf-8')
	
	if message == "ECU_HOSTNAME_REQUEST":
		server_socket.sendto(str.encode(hostname), address)
	if message == "ECU_SHUTDOWN":
		server_socket.close()
		break

os.system("shutdown /s /t 1")
