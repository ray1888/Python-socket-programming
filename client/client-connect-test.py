import socket
import os
import sys
import re
import random

class Control():
    def __init__(self):
        self.s = socket.socket()    #控制信道
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
            return tranport  #tranport为主动模式下被服务器连接的端口

    def actiondecide(self, mode):
        if re.match("put", cmd):  # 此处输入的命令为"put 绝对路径/文件"
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            filesize = os.path.getsize(filename)
            if mode == b"PASV":
                self.send(self.tunnel_sock, filename, filesize)
            else:
                self.send(self.tunnel_sock, filename, filesize, self.s)
        elif re.match("get", cmd):  # 此处输入的命令为"get 文件"
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            if mode == b"PASV":
                self.receive(self.tunnel_sock, filename)
            else:
                self.receive(self.tunnel_sock_active, filename, self.s)
        else:  # 其他的命令处理
            if mode == b"PASV":
                receive_content = self.tunnel_sock.recv(1024)
                print(receive_content)
            else:
                receive_content_size = self.s.recv(1024)  # 使用控制信道进行传输大小的确定
                received_size = 0
                show_data = ""
                while received_size > receive_content_size:
                    receive_content = self.tunnel_sock_active.recv(1024)  # 使用数据通道进行ls等操作的数据传输
                    show_data += receive_content
                self.tunnel_sock_active.close()
                print(show_data)



    def InputCmd(self, mode, shost, lport=None, laddr=None):
        cmd = input("请输入命令")
        self.s.send(bytes(cmd, encoding="utf-8"))
        print("cmd sent")

        if mode == "PASV":  #被动模式,数据通道传输模式
            serverport = self.s.recv(1024)
            serverport = int(serverport)
            print(serverport)
            tunnel_sock = socket.socket()
            tunnel_sock.connect((shost, serverport))   #被动模式的数据信道socket,name=tunnel_sock
            msg = tunnel_sock.recv(1024)
            print(msg)
            self.tunnel_sock = tunnel_sock
            self.actiondecide(self.mode)


        else:  #主动模式,数据通道传输模式
            tport = self.CreatePort(lport)   #tport是传输信道的端口
            self.s.send(bytes(str(tport), encoding="utf-8"))
            tsactive0 = socket.socket()  #tsactive0为等待对方进入的socket
            tsactive0.bind((laddr, tport))
            tsactive0.listen(5)
            tunnel_sock_active, addrr =tsactive0.accept()    #主动模式下的数据信道socket,tunnel_sock_active
            self.tunnel_sock_active = tunnel_sock_active
            msg_tun = self.tunnel_sock_active.recv(1024)
            print(msg_tun)
            """
            if re.match("put", cmd):   #此处输入的命令为"put 绝对路径/文件"
                cmd_split = cmd.split(" ")
                filename = cmd_split[1]
                filesize = os.path.getsize(filename)
                self.send(self.tunnel_sock, filename, filesize, self.s)
            elif re.match("get", cmd):  #此处输入的命令为"get 文件"
                cmd_split = cmd.split(" ")
                filename = cmd_split[1]
                self.receive(self.tunnel_sock_active, filename, self.s)
            else:  #其他的命令处理
                receive_content_size = self.s.recv(1024)   #使用控制信道进行传输大小的确定
                received_size = 0
                show_data = ""
                while received_size > receive_content_size:
                    receive_content = self.tunnel_sock_active.recv(1024)  #使用数据通道进行ls等操作的数据传输
                    show_data += receive_content
                self.tunnel_sock_active.close()
                print(show_data)
            """
            self.actiondecide(self.mode)

    def send(self, datasocket, file, filesizes, communicate_socket):
        communicate_socket.send(bytes(str(filesizes), encoding="utf-8")) #使用通信信道通信上传文件的大小
        with open(file, "rb") as f:
            send_size = 0
            while filesizes > send_size:
                data = f.read(1024)
                send_size += 1024
                datasocket.send(data)
        datasocket.close()
        communicate_socket.send(b"File upload complete")
        print("Put has been complete,Data Tunnel has been shut down")

    def receive(self, datasocket, filename):
        filesize = self.s.recv(1024)  #使用通信通道通信下载文件大小
        getsize = 0
        with open(self.pwd + "/" + filename, "ab") as f:
            while filesize > getsize:
                data = datasocket.recv(1024)
                f.write(data)
                data += 1024
        datasocket.close()
        print("Receive has been complete,Data Tunnel has been shut down")


if __name__ == "__main__":
    c = Control()


