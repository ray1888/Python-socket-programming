import socket
import json


port = 8101

content = s.recv(1024)
print(content)
print(s)
state = True

while state:
    cmd = input('请输入命令')
    print(cmd)
    print(type(cmd))
    s.send(bytes(cmd, encoding="utf-8"))
    result = s.recv(1024)
    print(result)
    if result == b"0":
        state = False
        print("you are quit")


class Control():

	def getconfig(self):
		Path = os.getcwd()
		with open(Path+'/clientconfig.json','r') as f:
			config = f.read()
			config = json.loads(config)
			host = config["host"]
			port = config["port"]
		return (host,port)

	def connect(self):
		host,port = getconfig()
		s = socket.socket()
		s.connect((host, port))
		

