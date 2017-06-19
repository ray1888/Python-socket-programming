import selectors
import socket
import re
import os
import random
import sys


class Control(object):
    def __init__(self, mode):
        self.mode = mode
        self.sel = selectors.DefaultSelector()
        self.topdir = "E:/FTP/"  # 下一版本会修改为使用配置文件进行设定
        self.workdir = self.topdir
        self.tmpdir = self.topdir + "TMP/"  # tmpdir、workdir、topdir最后会使用配置文件进行控制
        self.sock = socket.socket()
        self.host = '0.0.0.0'
        self.listenport = 25699
        self.sock.setblocking(False)
        self.sock.bind((self.host, self.listenport))
        self.sock.listen(100)
        self.sel.register(self.sock, selectors.EVENT_READ, self.accept)
        while 1:
            events = self.sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)

    def accept(self, communicate_socket, mask):
        client_sock, addr = communicate_socket.accept()
        print('accepted', client_sock, 'from', addr)
        client_sock.setblocking(False)
        self.client_sock = client_sock
        self.sel.register(self.client_sock, selectors.EVENT_READ, self.cmdread)

    def cmdread(self, client_sock, mask):
        command = client_sock.recv(1024)
        command = command.decode("ascii")
        print(command)
        if command == 'quit':
            self.sel.unregister(client_sock)
            client_sock.close()
        elif command == "ls":
            A = Action()
            self.sel.modify(client_sock, selectors.EVENT_WRITE, A.lsdir(client_sock, self.sel, self))
            # self.sel.modify(client_sock, selectors.EVENT_READ, self.accept)
        elif command == "pwd":
            A = Action()
            self.sel.modify(client_sock, selectors.EVENT_WRITE, A.pwd(client_sock, self.workdir))

        elif re.match('cd', command):
            split_cmd = command.split(" ")
            dirname = split_cmd[1]
            A = Action()
            k = self.sel.modify(client_sock, selectors.EVENT_WRITE,\
                            A.changedir(self.workdir, self.topdir, dirname, client_sock))
            print("k:{}".format(k.data))
            self.workdir = k.data
            print(self.workdir)

        elif re.match('put', command):
            split_cmd = command.split(" ")
            filename = split_cmd[1]
            A = Action()
            self.tranfer_tunnel(client_sock)
            self.sel.modify(client_sock, selectors.EVENT_WRITE,\
                            A.put(self.workdir, filename, client_sock, self.tunnel_sock))
            self.tunnel_sock.close()  # 关闭数据通道

        elif re.match('get', command):
            split_cmd = command.split(" ")
            filename = split_cmd[1]
            A = Action()
            self.tranfer_tunnel(client_sock)
            self.sel.modify(client_sock, selectors.EVENT_WRITE,\
                            A.get(self.workdir, filename, client_sock, self.tunnel_sock))
            self.tunnel_sock.close()  # 关闭数据通道

        elif re.match('mkdir', command):
            split_cmd = command.split(" ")
            dirname = split_cmd[1]
            A = Action()
            self.sel.modify(client_sock, selectors.EVENT_WRITE, A.mkdir(client_sock, dirname, self.workdir))

        self.sel.modify(client_sock, selectors.EVENT_READ, self.cmdread)

    def createPort(self):
        tranport = random.randint(30000, 65535)
        return tranport  #tp为主动模式下被服务器连接的端口

    def tranfer_tunnel(self, communicate_socket):
        mode = self.mode
        if mode == "1":
            tport = self.createPort()  # tport是传输信道的端口
            communicate_socket.send(bytes(str(tport), encoding="utf-8"))  # 发送端口给对方接入
            tunnel_sock_client = socket.socket()  # tunnel_sock为等待对方进入的socket
            tunnel_sock_client.bind((self.host, tport))
            tunnel_sock_client.listen(5)
            tunnel_sock, addrr = tunnel_sock_client.accept()
            self.tunnel_sock = tunnel_sock  # 此处tunnel_sock 为被动模式下的数据信道
        if mode == "2":
            client_host = communicate_socket.getpeername()[0]
            lport = 20
            serverport = communicate_socket.recv(1024)
            serverport = int(serverport)
            self.tunnel_sock = socket.socket()  # 此处tunnel_sock 为主动模式下的数据通道
            self.tunnel_sock.bind((self.host, lport))
            self.tunnel_sock.connect((client_host, serverport))


class Action(object):
    def lsdir(self, client_sock, selector, control):
        dircontent = os.listdir('E:/FTP')
        data = ''
        for item in dircontent:
            data += (item+'\n')
        client_sock.send(bytes(data, encoding="utf-8"))

    def pwd(self, communicate_socket, workpath):
        path = workpath
        print("path is {}".format(path))
        print(type(path))
        pathsize = sys.getsizeof(path)
        data = "600||" + str(pathsize) + "||" + path
        communicate_socket.send(bytes(data, encoding="utf-8"))

    def mkdir(self, communicate_socket, dirname, workdir):
        if os.path.exists(workdir + dirname + '/'):
            communicate_socket.send(b'501')
        else:
            os.mkdir(workdir+dirname+'/')
            communicate_socket.send(b'500')

    def changedir(self, workpath, toppath, dir, communicate_socket):
        if dir == "/":  # 跳转到共享的根目录,ok
            communicate_socket.send(b'300')
            communicate_socket.send(bytes(toppath))
            return toppath
        elif dir == "..":
            upper_dir = os.path.dirname(workpath[:-1])
            communicate_socket.send(b'300')
            communicate_socket.send(bytes(upper_dir, encoding="utf-8"))
            return upper_dir
        elif dir == ".":
            communicate_socket.send(b'300')
            communicate_socket.send(bytes(workpath, encoding="utf-8"))
            return workpath
        else:
            full_chdir = workpath + dir + "/"
            print("full_chdir :{}".format(full_chdir))
            former_dir = workpath
            if os.path.exists(full_chdir):
                if (toppath in full_chdir) or (toppath == full_chdir):
                    if os.path.isdir(full_chdir):
                        communicate_socket.send(b'300')
                        communicate_socket.send(bytes(workpath, encoding="utf-8"))
                        return full_chdir
                    else:
                        communicate_socket.send(b'303') #跳转到的不是文件夹，返回状态码303
                        return workpath
                else:
                    communicate_socket.send(b'302') #超过顶级目录的状态码
                    return workpath
            else:
                communicate_socket.send(b'301') #当前工作目录中不存在此目录
                return workpath

    def put(self, workpath, filename, communicate_socket, data_socket):
        print("filename :".format(filename))
        print(type(filename))
        filename = os.path.basename(filename)
        print("filename1:{}".format(filename))
        if os.path.exists(workpath + filename):
            communicate_socket.send(b"101")  # put失败状态码为101
        else:
            communicate_socket.send(b'100')
            print("filename = {}".format(filename))
            print(type(filename))
            # filesize = communicate_socket.recv(1024)
            while 1:
                try:
                    filesize = communicate_socket.recv(1024)
                    if filesize:
                        break
                except Exception:
                    continue
            print("filesize {}".format(filesize))
            filesize = int(filesize)
            print("filename1 = {}".format(filename))
            print(type(filesize))
            received_size = 0
            with open(workpath+filename, 'wb') as f:
                while filesize > received_size:
                    print(received_size)
                    data = data_socket.recv(1024)
                    f.write(data)
                    received_size += 1024
            print(b'File upload finish,Data tunnel shutdown,status code =100')


    def get(self, workpath, filename, communicate_socket, data_socket):
        sent_data_size = 0
        print("workdir = {}".format(workpath))
        filesize = os.path.getsize(workpath+filename)
        communicate_socket.send(b'200')
        communicate_socket.send(bytes(str(filesize), encoding="utf-8"))
        with open(workpath+filename, 'rb') as f:
            while filesize > sent_data_size:
                data = f.read(1024)
                sent_data_size += 1024
                data_socket.send(data)
        print("File Transfer Finish, status code=200")



if __name__ == "__main__":
    mode = input("请输入FTP服务器的模式：2为主动，1为被动")
    c = Control(mode)


