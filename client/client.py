import socket
import json
import os
import re
from random import randint

class Control():
	def __init__(self,mode):
		self.mode = mode
		self.s = socket.socket()   #此处s为控制信道的socket
		self.pwd = os.getcwd()
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
		socket.connect((host, port))
		content = socket.recv(1024)
		print(content)

	def Createport():
		dataport = randint(1024,65535)
		if dataport == socport:
			Createport()
		else:
			return dataport

	def InputCmd(self,socket):   #此处使用的是控制信道
		state = True
		addr, socport = socket.getsockname()
		dataport = Createport()
		while state:
			cmd = input('请输入命令')
			socket.send(bytes(cmd, encoding="utf-8"))  ##传输命令到服务器端
    		result = socket.recv(1024)
    		if result == b"0":
        		state = False
        		print("you are quit")
        	else:
    			DataTranfer(dataport,host,cmd)
    		

    def DataTranfer(self,port1,host,cmd):
    	pwd = self.pwd
    	self.ts = socket.socket()  #此处ts为传输信道的socket
    	ts = self.ts
    	ts.bind((host,port1))
    	ts.listen(5)
    	tsc, addr = ts.accept()
    	if re.match("upload",cmd):
    		cmd_split = cmd.split(" ")
    		filepath = cmd_split[1]
    		Send(tsc,filepath)
    	elif re.match("download",cmd):
    		cmd_split = cmd.split(" ")
    		filename = cmd_split[1]
    		Receive(tsc,pwd,filename)
    	else:
    		Flag = True
    		total_data
    		while Flag:
    			data = tsc.recv(1024)
    			if data == "":
    				break
    			else:
    				total_data += data
    		print(total_data)
		
    def Receive(self,datasocket,path,filename):    ##下载功能使用此方法,因为使用的是数据通道
    	Flag = True
    	while Flag:
    		with open(self.pwd+"/"+filename,"ab") as f:
    			data = datasocket.recv(1024)
    			if data == "":
    				break
    			else:
    				f.write(data)
    	datasocket.close()
    	print("Receive has been complete,Data Tunnel has been shut down")

    def Send(self,datasocket,filepath):   #只有上传功能才会使用此方法,因为使用的是数据通道
    	with open(filepath,"rb") as f:
    		Blank = True
    		while Blank:
    			data = f.read(1024)
    			if data == "":
    				Blank = False
    			else:
    				datasocket.send(data)
    	datasocket.close()
    	print("Send has been complete,Data Tunnel has been shut down")





