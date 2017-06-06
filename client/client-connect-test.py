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

    def Modeselection(self):
        mode = input("请输入模式，主动输入ACT，被动输入PASV")
        if mode != "ACT" and mode != "PASV":
            Modeselection()
        else:
            self.mode = mode

    def Connect(self,socket,mode):
        print(mode)
        host = "127.0.0.1"
        port = 21
        self.host = host
        socket.connect((host, port))
        welcome = socket.recv(1024)
        print(welcome)
        a, lport = socket.getsockname()
        self.lport = lport
        self.addr = a

    def CreatPort(self,localport):
        tranport = random.randint(4096,65535)
        if tranport == localport:
            CreatPort()
        else:
            return tranport  #tp为主动模式下被服务器连接的端口

    def InputCmd(self,socket,mode,shost,lport=None,laddr=None):
        cmd = raw_input("请输入命令")
        if mode == "PASV":  #被动模式
            serverport = socket.recv(1024)
            ts = socket.socket()
            ts.connect((shost, serverport))
            self.tssock = ts

        else:  #主动模式
            tport = CreatPort(lport)   #tport是传输信道的端口
            tsactive0 = socket.socket()  #tsactive0为等待对方进入的socket
            tsactive0.bind((laddr, tport))
            tsactive0.listen(5)
            tsactive1, addrr =tsactive0.accept()
            self.tssock = tsactive1
            msg_tun = tsactive1.recv(1024)



if __name__ == "__main__":
    c = Control()


