import socket
import os
import sys
import re
import random

class Control():
    def __init__(self):
        timeout = 200
        self.s = socket.socket()
        self.s.settimeout(timeout)
        self.topdir = "E:/FTP/"        #下一版本会修改为使用配置文件进行设定
        self.workdir = self.topdir
        self.tmpdir = self.topdir+"/TMP"   #tmpdir、workdir、topdir最后会使用配置文件进行控制
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

    def actiondecide(self, Action, cmd, mode):   #命令选择
        if re.match("put", cmd):
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            print("action filename:{}".format(filename))
            print(type(filename))
            if mode == "PASV":
                Action.put(self.workdir, filename, self.conn, self.tunnel_sock)
            else:
                Action.put(self.workdir, filename, self.conn, self.tunnel_sock)

        elif re.match("get", cmd):
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            print(filename)
            if mode == "PASV":
                Action.get(self.workdir, filename, self.conn, self.tunnel_sock)
            else:
                Action.get(self.workdir, filename, self.conn, self.tunnel_sock)
            self.tunnel_sock.close()      #关闭数据通道
            print("tunnel_sock_close")
        elif cmd == "ls":
            Action.lsdir(self.conn, self.workdir)
        elif re.match("cd", cmd):
            result = Action.cd(self.conn, cmd, self.topdir)
            result = result.split(" ")
            result_status = result[0]
            result_path = result[1]
            self.conn.send(bytes(result_status, encoding="utf-8"))
            if result_path != "":
                pathsize = os.path.getsize(result_path)
                self.conn.send(bytes(str(pathsize), encoding="utf-8"))
                self.conn.send(bytes(result_path, encoding="utf-8"))

        elif re.match("mkdir", cmd):
            Action.mkdir(self.conn, cmd, self.workdir)
        elif cmd == "pwd":
            Action.pwd(self.conn, self.workdir)



    def CmdRec(self, mode, chost, laddr=None):
        Flag = True
        while Flag:
            print(self.conn.getsockname())
            cmd = self.conn.recv(1024)
            cmd = cmd.decode("utf-8")
            print("cmd = {}".format(cmd))
            print(type(cmd))

            if cmd == "quit":   #进行quit命令判断
                self.conn.close()
                print("Control tunnel has been shut down, the FTP Server quit")
                break

            if mode == "PASV":  #被动模式
                tport = self.CreatPort()  # tport是传输信道的端口
                print("peer={}".format(self.conn.getpeername()))
                print("tport = {}".format(tport))
                self.conn.send(bytes(str(tport), encoding="utf-8"))
                tsactive0 = socket.socket()  # tsactive0为等待对方进入的socket
                tsactive0.bind((laddr, tport))
                tsactive0.listen(5)
                tunnel_sock, addrr = tsactive0.accept()  #此处tunnel_sock 为被动模式下的数据信道
                tunnel_sock.send(b"PASV mode tunnel has been started")
                self.tunnel_sock = tunnel_sock     #此处tunnel_sock 为被动模式下的数据信道
                #msg_tun = tsactive1.recv(1024)
                Active_A = Action()
                self.actiondecide(Active_A, cmd, self.mode)

            else: #主动模式
                lport = 20
                serverport = self.conn.recv(1024)
                print("serverport = {}".format(serverport))
                serverport = int(serverport)
                print("serverport = {}".format(serverport))
                print(type(serverport))
                print("lport = {}".format(lport))
                print("laddr = {}".format(laddr))
                self.tunnel_sock = socket.socket()    #此处tunnel_sock 为主动模式下的数据通道
                self.tunnel_sock.bind((laddr, lport))
                self.tunnel_sock.connect((chost, serverport))
                self.tunnel_sock.send(b"active mode tunnel has been started")
                Active_A = Action()
                self.actiondecide(Active_A, cmd, self.mode)
                self.tunnel_sock.close()  # 关闭数据通道
                print("tunnel_sock_close")
                print("lport {} is close".format(lport))


class Action():   #操作类，具体存放FTP服务器允许的操作
    def put(self, workdir, filename, communicate_socket, data_socket):
        print("filename :".format(filename))
        print(type(filename))
        filename = os.path.basename(filename)
        print("filename1:{}".format(filename))
        #filename = filename.split("/")
        #print("filename :".format(filename))
        if os.path.exists(workdir+filename):
            #communicate_socket.send(b"0")
            communicate_socket.send(b"101") #put失败状态码为101
        else:
            communicate_socket.send(b"trying to receive File")
            print("filename = {}".format(filename))
            print(type(filename))
            filesize = communicate_socket.recv(1024)
            filesize = int(filesize)
            print("filename1 = {}".format(filename))
            print(filesize)
            received_size = 0
            with open(workdir+"/"+filename, 'wb') as f:
                while filesize > received_size:
                    print(received_size)
                    data = data_socket.recv(1024)
                    f.write(data)
                    received_size += 1024

            print(b'File upload finish,Data tunnel shutdown,status code =100')
            communicate_socket.send(b'100')  #put成功状态码为100

    def get(self, workdir, filename, communicate_socket, data_socket):
        sent_data_size = 0
        filesize = os.path.getsize(workdir+filename)
        communicate_socket.send(bytes(str(filesize), encoding="utf-8"))
        with open(workdir+filename, 'rb') as f:
            while filesize > sent_data_size:
                data = f.read(1024)
                sent_data_size += 1024
                data_socket.send(data)
        print("File Transfer Finish, status code=200")
        communicate_socket.send(b'200')


    def lsdir(self, communicate_socket, workdir):
        dir_list = os.listdir(workdir)
        dirlist = ""
        for i in dir_list:
            print(i)
            dirlist += i+"\n"
        con_len = sys.getsizeof(dirlist)
        print("dirlist = {}".format(dirlist))
        communicate_socket.send(b"400")    #ls成功状态码400
        communicate_socket.send(bytes(str(con_len), encoding="utf-8"))   #发送传输内容大小
        if (con_len % 1024) != 0 and (con_len / 1024) != 0:  # 进行大小判断，保证能够传完
            times = int(con_len/1024)
            print(times)
            with open(workdir+"TMP/"+'tmp.txt', "w") as f:
                f.write(dirlist)
            with open(workdir+"/TMP/"+'tmp.txt', "rb") as f:
                for i in range(times + 1):
                    dir_list_div = f.read(1024)
                    communicate_socket.send(dir_list_div)
        else:
            communicate_socket.send(dir_list)

    def mkdir(self, communicate_socket, cmd, workdir):
        cmd_split = cmd.split(" ")
        Directory = cmd_split[1]
        #communicate_socket.send(b"4")
        if os.path.exists(workdir+"/"+Directory):
            communicate_socket.send(b"501")   #使用501状态码进行文件夹存在的状态码
        else:
            os.makedirs(workdir+"/"+Directory)
            communicate_socket.send(b"500")   #使用500状态码表示文件夹创建成功

    def pwd(self, communicate_socket, workpath):
        path = workpath
        print("path is {}".format(path))
        print(type(path))
        pathsize = sys.getsizeof(path)
        communicate_socket.send(b"600")   #pwd成功状态码
        communicate_socket.send(bytes(str(pathsize), encoding="utf-8"))
        communicate_socket.send(bytes(path, encoding="utf-8"))


    def cd(self, communicate_socket, cmd, topdir, workdir):
        cmd_split = cmd.split(" ")
        path = cmd_split[1]
        chdir = workdir+path
        chdir_path = os.path.dirname(chdir)
        if os.path.exists(chdir):
            if topdir in chdir_path:
                if os.path.isdir(chdir):
                    return "300 "+path
                else:
                    return "303 "  #跳转到的不是文件夹，返回状态码303
            else:
                return "302 " #超过顶级目录的状态码
        elif path == "..":
                upper_dir = os.path.dirname(workdir)
                return "300 "+upper_dir
        elif path == ".":
                return "300 "+workdir
        elif path == "/":
                return "300 "+topdir
        else:
            return "301 "  ##当前工作目录中不存在此目录


if __name__ == "__main__":
    c = Control()