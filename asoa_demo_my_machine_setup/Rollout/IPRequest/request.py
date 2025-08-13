import time
import socket
import select
import argparse


from concurrent import futures

PORT=4450

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.settimeout(1.0)
request = b'ECU_HOSTNAME_REQUEST'

timeout_in_seconds=1


def request_ecu(target_ip):
	try:
		socket.inet_aton(target_ip)
	except socket.error:
		return {"error":"Illegal IP: "+target_ip}

	try:
		target_addr = (target_ip, PORT)
		client_socket.sendto(request, target_addr)
		#ready = select.select([client_socket], [], [], timeout_in_seconds)
		data, server_addr = client_socket.recvfrom(1024)
		data=data.decode('utf-8')
		server_ip, server_port=server_addr
		return {data:server_ip}
	except socket.timeout:
		return {"warning":"No reply from "+target_ip}


parser = argparse.ArgumentParser()
parser._action_groups.pop()
required = parser.add_argument_group('required arguments')
required.add_argument('--subnet', required=True)
required.add_argument('--ip_start', required=True)
required.add_argument('--ip_end', required=True)

args=parser.parse_args()
arguments=vars(args)
subnet = arguments['subnet']
ip_start = int(arguments['ip_start'])
ip_end=int(arguments['ip_end'])


tasks=list()
with futures.ProcessPoolExecutor() as pool:

	for i in range(ip_start, ip_end+1):
		target_ip=subnet+str(i)
		tasks.append(pool.submit(request_ecu, target_ip))


	pool.shutdown(wait=True)

res_str = ""
for f in tasks:
	f_res = f.result()
	if f_res != None:
		res_str+=list(f_res.keys())[0]+";"+list(f_res.values())[0]+"|"

res_str=res_str[:-1]

print(res_str)
