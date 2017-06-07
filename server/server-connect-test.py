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
            tunnal_sock = socket.socket()
            tunnal_sock.bind((laddr, lport))
            tunnal_sock.connect((chost, serverport))
            tunnal_sock.send(b"active mode tunnel has been started")
            self.tssock = tunnal_sock


if __name__ == "__main__":
    c = Control()