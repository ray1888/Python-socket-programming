import socket
import os
import sys
import threading
import random
import re


class Action():
    def __init__(self,mode,workdir):
        self.ts = socket.socket()
        self.mode = mode
        self.workdir = workdir
        if self.mode == b"active":
            self.port = 20
        else:
            self.port=random.randint(1024,65535)

    def CreateSocket(self):

    def upload(self,filename,c):
        with open(workdir+'filename','ab') as f:
            while True:
                try:
                    data = c.recv(1024)
                except exception:
                    print('end')
                    print(b'File upload finish')
                    c.send(b'File upload finish')
                    break
                '''
                暂时采用错误机制进行文件传输判断，之后可能改为在最后一个包时加上一段特定符号进行判断
                '''
                f.write(data)

    def download(self,filename,c):
        with open(workdir + 'filename', 'rb') as f:
            while True:
                data = f.read(1024)
                if data != "":
                    c.send(data)
                else:
                    print("File Transfer Finish")
                    c.send(b'File Transfer Finish')
                    break

    
    def lsdir(self,c):
        dir_list = os.listdir(self.workdir)
        con_len = sys.getsizeof(dir_list)
        if (con_len%1024) != 0 and (con_len/1024) != 0:   #进行判断，防止list的目录大于1024字节，保证能够传完
            times = con_len/1024
            with open(workdir+'/tmp.txt',"wb") as f:
              f.write(dir_list)
            with open(workdir+'/tmp.txt',"rb") as f:
              for i in range(times+1):
                  dir_list_div = f.read(1024)
                  c.send(dir_list_div)
        else:
            c.send(dir_list)
    

    def mkdir(self,c,new_name):
        try:
            os.mkdir(self.workdir+new_name)
            c.send(b'Directory is created')
        except Exception:
            c.send(b'The Directory is already exist')

    def cwdir(self,c):
        path = os.getcwd()
        c.send(bytes(path))

    '''
    def chdir(self,path_son):
        os.chdir(self.workdir+)
    '''

class Control():
    def __init__(self,ip,s,dir,mode):
        self.s = socket.socket()
        Eatabalish()
        self.workdir = dir
        self.action(self.conn)

    def Eatabalish(self,s):
        ip = str(ip)
        port='21'
        s.bind((ip, port))
        s.listen(5)
        conn, addr = s.accept()
        self.conn = conn
        c = self.conn
        print("addr={}".format(addr))
        print("socketc={}".format(c))
        c.send(b'You are already connect in server')

    def action(self,c):
       while True:
           act = c.recv(1024)
           A = Action(self.workdir,self.mode)
           if act == "lsdir":
               A.lsdir(c)
           if re.match("mkdir",act):
               splita = act.split(":")
               dirname = splita[1]
               A.mkdir(dirname,c)
           if re.match("download",act):
               splita = act.split(":")
               file = splita[1]
               A.download(file,c)
           if re.match("upload",act):
               splita = act.split(":")
               file = splita[1]
               A.upload(file,c)
           if act == 'quit':
               print("out")
               c.send(bytes('0', encoding="utf-8"))
               c.close()
               break









