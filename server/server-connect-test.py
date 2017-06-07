import socket
import os
import sys
import re
import random

class Control():
    def __init__(self):
        self.s = socket.socket()
        self.pwd = os.getcwd()
        self.Connect()
        self.CmdRec(self.mode, self.rmaddr, self.host)

    def Connect(self):
        host = "0.0.0.0"
        port = 21
        self.s.bind((host, port))
        self.s.listen(5)
        c ,addr = self.s.accept()
        self.conn = c
        c.send(b"Welcome to the FTP server")
        mode = c.recv(1024)
        print("mode is {}".format(mode))   #从client接收到的Mode参数
        self.mode = mode
        rmport = addr[1]
        rmaddr = addr[0]
        self.rmport = rmport
        self.rmaddr = rmaddr
        host, lport = self.conn.getpeername()
        self.host = host
        print(self.rmport)
        print(self.rmaddr)
        print(self.host)


    def CreatPort(self):
        tranport = random.randint(30000, 65535)
        return tranport  #tp为主动模式下被服务器连接的端口

    def CmdRec(self, mode, chost, laddr=None):
        print(self.conn.getsockname())
        cmd = self.conn.recv(1024)
        print(cmd)
        if mode == b"PASV":  #被动模式
            tport = self.CreatPort()  # tport是传输信道的端口
            print("peer={}".format(self.conn.getpeername()))
            self.conn.send(bytes(str(tport), encoding="utf-8"))
            tsactive0 = socket.socket()  # tsactive0为等待对方进入的socket
            tsactive0.bind((laddr, tport))
            tsactive0.listen(5)
            tsactive1, addrr = tsactive0.accept()
            tsactive1.send(b"PASV mode tunnel has been started")
            self.tssock = tsactive1
            #msg_tun = tsactive1.recv(1024)

        else: #主动模式
            lport = 20
            serverport = self.conn.recv(1024)
            print(serverport)
            serverport = int(serverport)
            print(type(serverport))
            tunnel_sock = socket.socket()
            tunnel_sock.bind((laddr, lport))
            tunnel_sock.connect((chost, serverport))
            tunnel_sock.send(b"active mode tunnel has been started")
            self.tssock = tunnel_sock

class Action():
    def upload(self, workdir, filename, c):
        with open(workdir + 'filename', 'ab') as f:
            while True:
                try:
                    data = c.recv(1024)
                except Exception:
                    print('end')
                    print(b'File upload finish')
                    c.send(b'File upload finish')
                    break
                '''
                暂时采用错误机制进行文件传输判断，之后可能改为在最后一个包时加上一段特定符号进行判断
                '''
                f.write(data)

    def download(self, workdir, filename, c):
        with open(workdir + 'filename', 'rb') as f:
            while True:
                data = f.read(1024)
                if data != "":
                    c.send(data)
                else:
                    print("File Transfer Finish")
                    c.send(b'File Transfer Finish')
                    break

    def lsdir(self, c, workdir):
        dir_list = os.listdir(workdir)
        con_len = sys.getsizeof(dir_list)
        if (con_len % 1024) != 0 and (con_len / 1024) != 0:  # 进行判断，防止list的目录大于1024字节，保证能够传完
            times = con_len / 1024
            with open(workdir + '/tmp.txt', "wb") as f:
                f.write(dir_list)
            with open(workdir + '/tmp.txt', "rb") as f:
                for i in range(times + 1):
                    dir_list_div = f.read(1024)
                    c.send(dir_list_div)
        else:
            c.send(dir_list)

    def mkdir(self, c, new_name):
        try:
            os.mkdir(self.workdir + new_name)
            c.send(b'Directory is created')
        except Exception:
            c.send(b'The Directory is already exist')

    def cwdir(self, c):
        path = os.getcwd()
        c.send(bytes(path))



if __name__ == "__main__":
    c = Control()