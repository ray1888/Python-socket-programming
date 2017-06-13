import socket
import os
import sys
import re
import random
import threading

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
            self.Modeselection()
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
        tranport = random.randint(4096, 65535)
        if tranport == localport:
            self.CreatePort(localport)
        else:
            return tranport  #tranport为主动模式下被服务器连接的端口

    def actiondecide(self, mode, cmd):
        if re.match("put", cmd):  # 此处输入的命令为"put 绝对路径/文件"
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            filesize = os.path.getsize(filename)
            print("filename : {}".format(filename))
            print(type(filename))
            print("filesize : {}".format(filesize))
            print(type(filesize))
            if mode == "PASV":
                self.send(self.tunnel_sock, filename, filesize, self.s)
            else:
                self.send(self.tunnel_sock_active, filename, filesize, self.s)
        elif re.match("get", cmd):  # 此处输入的命令为"get 文件"
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            if mode == "PASV":
                self.receive(self.tunnel_sock, filename)
                self.s.recv(1024)
            else:
                self.receive(self.tunnel_sock_active, filename)
                self.s.recv(1024)
        else:  # 其他的命令处理,处理上传下载操作外，其余数据传输操作混合在控制信道中进行传输
            if cmd == "ls":
                status_code = self.recvstatuscode(self.s)
                print("statuscode = {}".format(status_code))
                print(type(status_code))
                status_code = int(status_code)
                print("statuscode = {}".format(status_code))
                content_size = self.contentsize(self.s)
                print("content_size={}".format(content_size))
                print(type(content_size))
                if status_code == 400:
                    data = self.cmdcontentrecv(content_size, self.s)
                    print("data : \n {}".format(data))
                    print("lsdir:\n {}".format(data))
            if re.match("cd", cmd):
                cmd_split = cmd.split(" ")
                Dir = cmd_split[1]
                status_code = self.recvstatuscode(self.s)
                status_code = int(status_code)
                if status_code == 300:
                    content_size = self.contentsize(self.s)
                    print("content_size:{}".format(content_size))
                    data = self.cmdcontentrecv(content_size, self.s)
                    print("you have change your directory to {}".format(Dir))
                else:
                    print("status code is {},please review the usebook".format(status_code))
            if cmd == "pwd":
                status_code = self.recvstatuscode(self.s)
                print("status_code:{}".format(status_code))
                content_size = self.contentsize(self.s)
                print("content_size:{}".format(content_size))
                data = self.cmdcontentrecv(content_size, self.s)
                print("current directory is {}".format(data))
            if re.match("mkdir", cmd):
                status_code = self.recvstatuscode(self.s)
                status_code = int(status_code)
                if status_code == 500:
                    cmd_split = cmd.split(" ")
                    dir_name = cmd_split[1]
                    print("{} has been created".format(dir_name))
                else:
                    print("the diretory has already creadted before")

    def recvstatuscode(self, communicate_socket):
        status_code = communicate_socket.recv(1024)
        print("status_code:{}".format(status_code))
        return status_code

    def contentsize(self, communicate_socket):   #把上面的通过接受命令结果返回大小过程封装成函数
        receive_content_size = communicate_socket.recv(1024)
        receive_content_size = int(receive_content_size.decode("utf-8"))
        return receive_content_size

    def cmdcontentrecv(self, content_size, communicate_socket):    #接受命令返回的结果
        received_size = 0
        show_data = ""
        while received_size < content_size:
            receive_content = communicate_socket.recv(1024)  # 使用控制通道进行ls等操作的数据传输
            receive_content = receive_content.decode("utf-8")
            received_size += 1024
            show_data += receive_content
        return show_data



    def InputCmd(self, mode, shost, lport=None, laddr=None):
        Flag = True
        while Flag:
            cmd = input("请输入命令")
            self.s.send(bytes(cmd, encoding="utf-8"))  #此处客户端已经把从用户接收到的命令传到了服务器端
            print(cmd)
            print("cmd sent")
            if cmd == "quit":   #进行quit命令判断
                self.s.close()
                print("Control tunnel has been shut down, the FTP Client quit")
                break
            elif cmd == "":
                Usage= """Usage: \
                          ls --listdir current dir \n  \
                          cd+' '+dir --change diretory to dir \n \
                          get filename --download file from server \n \
                          put LocalfilePath -- upload file to ftpserver \n \
                          pwd -- show current dir located \n \
                          mkdir --make diretory in ftp server \n \
                          quit  --quit from the ftpserver
                        """
                print(Usage)
                continue
            if mode == "PASV":  #被动模式,数据通道传输模式
                serverport = self.s.recv(1024)   #接收数据通道端口
                print("serverport = {}".format(serverport))
                serverport = int(serverport)
                print(serverport)
                tunnel_sock = socket.socket()
                tunnel_sock.connect((shost, serverport))   #被动模式的数据信道socket,name=tunnel_sock
                msg = tunnel_sock.recv(1024)
                print(msg)
                self.tunnel_sock = tunnel_sock
                self.actiondecide(self.mode, cmd)
            else:  #主动模式,数据通道传输模式
                tport = self.CreatePort(lport)   #tport是传输信道的端口
                self.s.send(bytes(str(tport), encoding="utf-8"))
                tsactive0 = socket.socket()  #tsactive0为等待对方进入的socket
                tsactive0.bind((laddr, tport))
                tsactive0.listen(5)
                tunnel_sock_active, addrr = tsactive0.accept()    #主动模式下的数据信道socket,tunnel_sock_active
                self.tunnel_sock_active = tunnel_sock_active
                msg_tun = self.tunnel_sock_active.recv(1024)
                print(msg_tun)
                self.actiondecide(self.mode, cmd)
                self.tunnel_sock_active.close()
                #tsactive0.close()

    def send(self, datasocket, file, filesizes, communicate_socket):
        exist = communicate_socket.recv(1024)
        print(exist)
        print(type(exist))
        if exist == b'101':
            print("the file already exist in FTP Server")
        else:
            communicate_socket.send(bytes(str(filesizes), encoding="utf-8")) #使用通信信道通信上传文件的大小
            with open(file, "rb") as f:
                send_size = 0
                while filesizes > send_size:
                    print(send_size)
                    data = f.read(1024)
                    send_size += 1024
                    datasocket.send(data)
            communicate_socket.recv(1024)
            print("Put has been complete,Data Tunnel has been shut down")

    def receive(self, datasocket, filename):
        filesize = self.s.recv(1024) #使用通信通道通信下载文件大小
        print(filesize)
        filesize = int(filesize)
        print(type(filesize))
        getsize = 0
        print(self.pwd)
        with open(self.pwd + "/" + filename, "ab") as f:
            while filesize > getsize:
                data = datasocket.recv(1024)
                f.write(data)
                getsize += 1024
        print("Receive has been complete,Data Tunnel has been shut down")


if __name__ == "__main__":
    c = Control()


