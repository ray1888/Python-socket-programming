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
        self.Connect(self.s, self.mode)
        self.InputCmd(self.s, self.mode, self.host, self.lport, self.addr)

    def Modeselection(self):
        mode = input("请输入模式，主动输入ACT，被动输入PASV")
        if mode != "ACT" and mode != "PASV":
            Modeselection()
        else:
            self.mode = mode

    def Connect(self, s, mode):
        print(mode)
        host = "127.0.0.1"
        port = 21
        self.host = host
        s.connect((host, port))
        welcome = s.recv(1024)
        print(welcome)
        modemsg = bytes(mode, encoding="utf-8")
        s.send(modemsg)
        a, lport = s.getsockname()
        self.lport = lport
        self.addr = a

    def CreatPort(self, localport):
        tranport = random.randint(4096,65535)
        if tranport == localport:
            CreatPort()
        else:
            return tranport  #tp为主动模式下被服务器连接的端口

    def InputCmd(self, s, mode, shost, lport=None, laddr=None):
        cmd = input("请输入命令")
        s.send(bytes(cmd, encoding="utf-8"))
        print("cmd sent")
        if mode == "PASV":  #被动模式
            serverport = s.recv(1024)
            print(serverport)
            ts = socket.socket()
            ts.connect((shost, serverport))
            msg = ts.recv(1024)
            print(msg)
            self.tssock = ts

        else:  #主动模式
            tport = CreatPort(lport)   #tport是传输信道的端口
            tsactive0 = socket.socket()  #tsactive0为等待对方进入的socket
            tsactive0.bind((laddr, tport))
            tsactive0.listen(5)
            tsactive1, addrr =tsactive0.accept()
            self.tssock = tsactive1
            msg_tun = tsactive1.recv(1024)
            print(msg_tun)



if __name__ == "__main__":
    c = Control()


