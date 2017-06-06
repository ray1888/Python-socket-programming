import socket
import os
import sys
import re


class Control():
    def __init__(self):
        self.s = socket.socket()
        self.pwd = os.getcwd()
        self.Connect(self.s)

    def Connect(self,socket):
        host = "127.0.0.1"
        port = 21
        socket.bind((host,port))
        socket.listen(5)
        c ,addr = socket.accept()
        self.conn = c
        c.send(b"Welcome to the FTP server")

    def CreatPort(self,localport):
        tranport = random.randint(4096,65535)
        if tranport == localport:
            CreatPort()
        else:
            return tranport  #tp为主动模式下被服务器连接的端口

    def CmdRec(self,socket,mode,shost,lport=None,laddr=None):
        cmd = socket.recv(1024)
        if mode == "PASV":  #被动模式
            tport = CreatPort(lport)  # tport是传输信道的端口
            tsactive0 = socket.socket()  # tsactive0为等待对方进入的socket
            tsactive0.bind((laddr, tport))
            tsactive0.listen(5)
            tsactive1, addrr = tsactive0.accept()
            self.tssock = tsactive1
            msg_tun = tsactive1.recv(1024)


        else:  #主动模式
            serverport = socket.recv(1024)
            ts = socket.socket()
            ts.connect((shost, serverport))
            self.tssock = ts


if __name__ == "__main__":
    c = Control()