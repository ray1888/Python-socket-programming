import socket
import os
import sys
import re
import random

class Control():
    def __init__(self):
        self.s = socket.socket()
        self.workdir = "E:\FTP"
        self.Connect()
        self.CmdRec(self.mode, self.rmaddr, self.host)

    def Connect(self):
        host = "0.0.0.0"
        port = 21
        self.s.bind((host, port))
        self.s.listen(5)
        c ,addr = self.s.accept()
        self.conn = c   ##self.conn 为控制信道与Client端通信的socket
        c.send(b"Welcome to the FTP server")
        mode = c.recv(1024)
        mode = mode.decode("utf-8")
        print("mode is {}".format(mode))   #从client接收到的Mode参数
        self.mode = mode
        rmport = addr[1]
        rmaddr = addr[0]
        self.rmport = rmport
        self.rmaddr = rmaddr
        host, lport = self.conn.getpeername()
        self.host = host


    def CreatPort(self):
        tranport = random.randint(30000, 65535)
        return tranport  #tp为主动模式下被服务器连接的端口

    def actiondecide(self, Action, cmd):
        if re.match("put", cmd):
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            print(filename)
            print(type(filename))
            Action.put(self.workdir, filename, self.conn, self.tunnel_sock)

        elif re.match("get", cmd):
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            Action.get(self.workdir, filename, self.conn, self.tunnel_sock)

        elif cmd == b"ls":
            os.listdir()


    def CmdRec(self, mode, chost, laddr=None):
        Flag = True
        while Flag:
            print(self.conn.getsockname())
            cmd = self.conn.recv(1024)
            cmd = cmd.decode("utf-8")
            print(cmd)
            print(type(cmd))

            if cmd == "quit":   #进行quit命令判断
                self.conn.close()
                print("Control tunnel has been shut down, the FTP Server quit")
                break

            if mode == "PASV":  #被动模式
                tport = self.CreatPort()  # tport是传输信道的端口
                print("peer={}".format(self.conn.getpeername()))
                self.conn.send(bytes(str(tport), encoding="utf-8"))
                tsactive0 = socket.socket()  # tsactive0为等待对方进入的socket
                tsactive0.bind((laddr, tport))
                tsactive0.listen(5)
                tunnel_sock, addrr = tsactive0.accept()  #此处tunnel_sock 为被动模式下的数据信道
                tunnel_sock.send(b"PASV mode tunnel has been started")
                self.tunnel_sock = tunnel_sock     #此处tunnel_sock 为被动模式下的数据信道
                #msg_tun = tsactive1.recv(1024)
                Active_A = Action()
                self.actiondecide(Active_A, cmd)

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
                self.tunnel_sock = tunnel_sock    #此处tunnel_sock 为主动模式下的数据通道
                Active_A = Action()
                self.actiondecide(Active_A, cmd)


class Action():
    def put(self, workdir, filename, communicate_socket, data_socket):
        filesize = communicate_socket.recv(1024)
        filesize = int(filesize)
        filename = filename.split("\\")[1]
        print(filename)
        print(filesize)
        received_size = 0
        with open(workdir+"\\"+filename, 'wb') as f:
            while filesize > received_size:
                print(received_size)
                data = data_socket.recv(1024)
                f.write(data)
                received_size += 1024
        data_socket.close()               #关闭数据通道
        print(b'File upload finish')
        communicate_socket.send(b'File upload finish')

    def get(self, workdir, filename, communicate_socket, data_socket):
        sent_data_size = 0
        filesize = os.path.getsize(workdir+filename)
        communicate_socket.send(bytes(filesize, encoding="utf-8"))
        with open(workdir+filename, 'rb') as f:
            while filesize>sent_data_size:
                data = f.read(1024)
                sent_data_size += 1024
                data_socket.send(data)
        data_socket.close()
        print("File Transfer Finish")
        communicate_socket.send(b'File Transfer Finish')


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