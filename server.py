import socket
import os
import sys
import threading
import random

while True:
    rec_str = c.recv(1024)
    print(c)
    print('rec_str={}'.format(rec_str))
    if rec_str == b'quit' or rec_str == b'q':
        print("out")
        c.send(bytes('0',encoding="utf-8"))
        c.close()
        break
    else:
        c.send(bytes('try another cmd ,it not dead', encoding="utf-8"))

class Action():
    def __init__(self,mode,workdir):
        self.mode = mode
        self.workdir = workdir
        if self.mode == b"active":
            self.port = 20
        else:
            self.port=random.randint(1024,65535)

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
        if (con_len%1024) != 0 and (con_len/1024) != 0:
            times = con_len/1024
            for i in range(times+1):
                dir_list_div = dir_list
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


    def chdir(self,path_son):

        os.chdir(self.workdir+)




class Control():
    def __init__(self,ip,s,dir,mode):
        ##s = socket.socket()
        self.workdir = dir
        ip = str(ip)
        port=21
        s.bind((ip, port))
        s.listen(5)

    def Eatabalish(self,s,c):
        ##c, addr = s.accept()
        print("addr={}".format(addr))
        print("socketc={}".format(c))
        c.send(b'You are already connect in server')

    def quit(self,c):
        rec_str = c.recv(1024)
        if rec_str == b'quit' or rec_str == b'q':
            print("out")
            c.send(bytes('0', encoding="utf-8"))
            c.close()
            break






