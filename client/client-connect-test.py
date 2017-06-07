import socket
import os
import sys
import re
import random

class Control():
    def __init__(self):
        self.s = socket.socket()
        self.pwd = os.getcwd()
        self.Modeselection()
        self.Connect(self.mode)
        self.InputCmd(self.mode, self.host, self.lport, self.addr)

    def Modeselection(self):
        mode = input("请输入模式，主动输入ACT，被动输入PASV")
        if mode != "ACT" and mode != "PASV":
            Modeselection()
        else:
            self.mode = mode

    def Connect(self, mode):
        print(mode)
        host = "127.0.0.1"
        port = 21
        self.host = host
        self.s.connect((host, port))
        welcome = self.s.recv(1024)
        print(welcome)
        modemsg = bytes(mode, encoding="utf-8")
        self.s.send(modemsg)   #把mode参数从client传到服务器
        a, lport = self.s.getsockname()
        self.lport = lport
        self.addr = a
        print(self.lport)
        print(self.addr)


    def CreatePort(self, localport):
        tranport = random.randint(4096,65535)
        if tranport == localport:
            self.CreatePort(localport)
        else:
            return tranport  #tp为主动模式下被服务器连接的端口

    def InputCmd(self, mode, shost, lport=None, laddr=None):
        cmd = input("请输入命令")
        self.s.send(bytes(cmd, encoding="utf-8"))
        print("cmd sent")
        if mode == "PASV":  #被动模式
            serverport = self.s.recv(1024)
            serverport = int(serverport)
            print(serverport)
            ts = socket.socket()
            ts.connect((shost, serverport))
            msg = ts.recv(1024)
            print(msg)
            self.tssock = ts
        else:  #主动模式
            tport = self.CreatePort(lport)   #tport是传输信道的端口
            self.s.send(bytes(str(tport), encoding="utf-8"))
            tsactive0 = socket.socket()  #tsactive0为等待对方进入的socket
            tsactive0.bind((laddr, tport))
            tsactive0.listen(5)
            tsactive1, addrr =tsactive0.accept()
            self.tssock = tsactive1
            msg_tun = tsactive1.recv(1024)
            print(msg_tun)

if __name__ == "__main__":
    c = Control()


