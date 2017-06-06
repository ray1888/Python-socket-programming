import socket
import json

class Control():
	def __init__(self):



	def Getconfig(self):
		Path = os.getcwd()
		with open(Path+'/clientconfig.json','r') as f:
			config = f.read()
			config = json.loads(config)
			host = config["host"]
			port = config["port"]
		return (host,port)

	def Connect(self):
		host,port = getconfig()
		s = socket.socket()
		s.connect((host, port))
		content = s.recv(1024)
		print(content)
	
	def InputCmd(self):
		state = True
		while state:
			cmd = input('请输入命令')
			s.send(bytes(cmd, encoding="utf-8"))
    		result = s.recv(1024)
    		if result == b"0":
        		state = False
        		print("you are quit")

    
		

