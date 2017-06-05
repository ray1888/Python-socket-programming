import socket
import json

s = socket.socket()
port = 8101
s.connect(("127.0.0.1", port))
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
		

