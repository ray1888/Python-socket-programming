import socket
import json

class Control():
	def __init__(self,mode):
		self.mode = mode
		self.s = socket.socket()
		self.Connect(self.s)
		self.InputCmd(self.s)

	def Getconfig(self):
		Path = os.getcwd()
		with open(Path+'/clientconfig.json','r') as f:
			config = f.read()
			config = json.loads(config)
			host = config["host"]
			port = config["port"]
		return (host,port)

	def Connect(self,socket):
		host,port = getconfig()
		s.connect((host, port))
		content = s.recv(1024)
	
	def InputCmd(self,socket):
		state = True
		while state:
			cmd = input('请输入命令')
			s.send(bytes(cmd, encoding="utf-8"))
    		result = s.recv(1024)
    		if result == b"0":
        		state = False
        		print("you are quit")

    def DataTranfer(self):
    	s = socket.socket()
    	Flag = True
    	while Flag:
    		data = s.recv(1024)

		

