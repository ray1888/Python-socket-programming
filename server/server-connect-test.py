import socket
import os
import sys
import re
import random
import threading
import asyncio

class Control():
    def __init__(self, loop):
        timeout = 200
        self.s = socket.socket()
        self.s.settimeout(timeout)
        self.topdir = "E:/FTP/"        #下一版本会修改为使用配置文件进行设定
        self.workdir = self.topdir
        self.tmpdir = self.topdir+"TMP/"   #tmpdir、workdir、topdir最后会使用配置文件进行控制
        self.loop = loop
        loop.create_task(self.connect(self.loop))

    async def createPort(self):
        tranport = random.randint(30000, 65535)
        return tranport  #tp为主动模式下被服务器连接的端口

    async def connect(self, loop):
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #socket的复用
        self.s.setblocking(0)
        host = "127.0.0.1"
        port = 21
        self.s.bind((host, port))
        self.s.listen(100)
        while 1:
            c ,addr = await loop.sock_accept(self.s)
            self.conn = c  ##self.conn 为控制信道与Client端通信的socket
            #c.send(b"Welcome to the FTP server")
            await loop.sock_sendall(self.conn, b"Welcome to the FTP server")
            mode = await loop.sock_recv(self.conn, 1024)
            mode = mode.decode("utf-8")
            self.mode = mode
            rmport = addr[1]
            rmaddr = addr[0]
            self.rmport = rmport
            self.rmaddr = rmaddr
            host, lport = self.conn.getpeername()
            self.host = host
            #self.CmdRec(self.mode, self.rmaddr, self.host)
            await loop.create_task(cmdrec(self.mode, self.rmaddr, self.host, self.loop, self.conn))


    async def cmdrec(self, mode, connect_host, local_addr=None, eventloop, communicate_socket):
        while 1:
            cmd = await loop.sock_recv(self.conn, 1024)
            cmd = cmd.decode("utf-8")
            if cmd == "quit":  # 进行quit命令判断
                self.conn.close()
                break
            if mode == "PASV" and (cmd == "put" or cmd == 'get'):  # 被动模式
                tport = await self.createPort()  # tport是传输信道的端口
                #communicate_socket.send(bytes(str(tport), encoding="utf-8"))  # 发送端口给对方接入
                loop.sock_sendall(communicate_socket, bytes(str(tport), encoding="utf-8"))
                tunnel_sock = socket.socket()  # tunnel_sock为等待对方进入的socket
                tunnel_sock.bind((local_addr, tport))
                tunnel_sock.listen(5)
                tunnel_sock_client, addrr = await loop.sock_accept(tsactive0)    #此处tunnel_sock_client为被动模式下的数据信道
                await loop.sock_sendall(tunnel_sock_client, b"PASV mode tunnel has been started")
                #tunnel_sock.send(b"PASV mode tunnel has been started")  #
                self.tunnel_sock = tunnel_sock_client  # 此处tunnel_sock 为被动模式下的数据信道
                # msg_tun = tsactive1.recv(1024)
                Active_A = Action()
                await self.actiondecide(Active_A, cmd, self.mode, communicate_socket)
            elif (cmd == "put" or cmd == 'get'):  # 主动模式
                lport = 20
                serverport = self.conn.recv(1024)
                serverport = int(serverport)
                self.tunnel_sock = socket.socket()  # 此处tunnel_sock 为主动模式下的数据通道
                self.tunnel_sock.bind((local_addr, lport))
                #self.tunnel_sock.connect((connect_host, serverport))
                await loop.sock_connect(self.tunnel_sock, connect_host)
                #self.tunnel_sock.send(b"active mode tunnel has been started")
                await loop.sock_sendall(self.tunnel_sock, b"active mode tunnel has been started")
                Active_A = Action()
                await self.actiondecide(Active_A, cmd, self.mode, communicate_socket)
                self.tunnel_sock.close()  # 关闭数据通道
            else:
                Active_A = Action()
                await self.actiondecide(Active_A, cmd, None, communicate_socket)


    async def actiondecide(self, Action, cmd, mode=None, communicate_socket):   #命令选择的入口
        if re.match("put", cmd):
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            print("action filename:{}".format(filename))
            print(type(filename))
            if mode == "PASV":
                await Action.put(self.workdir, filename, self.conn, self.tunnel_sock)
            else:
                await Action.put(self.workdir, filename, self.conn, self.tunnel_sock)
                
        elif re.match("get", cmd):
            cmd_split = cmd.split(" ")
            filename = cmd_split[1]
            print(filename)
            if mode == "PASV":
                await Action.get(self.workdir, filename, self.conn, self.tunnel_sock)
            else:
                await Action.get(self.workdir, filename, self.conn, self.tunnel_sock)
            self.tunnel_sock.close()      #关闭数据通道
            print("tunnel_sock_close")

        elif cmd == "ls":
            data = await Action.lsdir(self.conn, self.workdir, self.tmpdir)
            split_data = data.split("||")
            status_code = split_data[0]
            sendsize = split_data[1]
            content = split_data[2]

            if (sendsize % 1024) != 0 and (sendsize / 1024) != 0:  # 进行大小判断，保证能够传完
                times = int(sendsize / 1024)
                print(times)
                with open(self.tmpdir+'tmp.txt', "w") as f:
                    f.write(content)
                with open(self.tmpdir+'tmp.txt', "rb") as f:
                    for i in range(times + 1):
                        content_div = f.read(1024)
                        #communicate_socket.send(dir_list_div)
                        await loop.sock_sendall(communicate_socket, content_div)
            else:
                #communicate_socket.send(dir_list)
                await loop.sock_sendall(communicate_socket, content)

        elif re.match("cd", cmd):
            result = await Action.cd(cmd, self.topdir, self.workdir)
            result = result.split(" ")
            result_status = result[0]
            result_path = result[1]
            print("result_status type:{}".format(type(result_status)))
            self.conn.send(bytes(result_status, encoding="utf-8"))  #发送状态码
            if result_path != "":
                pathsize = len(result_path)
                print("result_path:{}".format(result_path))
                print("pathsize = {}".format(pathsize))
                self.workdir = result_path
                print("workdir = {}".format(self.workdir))
                #self.conn.send(bytes(str(pathsize), encoding="utf-8")) #发送目录名大小
                #self.conn.send(bytes(result_path, encoding="utf-8"))   #发送目录名称
                await loop.sock_sendall(communicate_socket, bytes(str(pathsize), encoding="utf-8"))
                await loop.sock_sendall(communicate_socket, bytes(result_path, encoding="utf-8"))

        elif re.match("mkdir", cmd):
            status_code =  await Action.mkdir(self.conn, cmd, self.workdir)
            await loop.sock_sendall(communicate_socket, status_code)

        elif cmd == "pwd":
            data = await Action.pwd(self.workdir)
            data_split = data.split("||")
            status_code = data_split[0]
            status_code = bytes(status_code, encoding="utf-8")
            size = data_split[1]
            size = bytes(size, encoding="utf-8")
            sendpath = data_split[2]
            sendpath = bytes(sendpath, encoding="utf-8")
            await loop.sock_sendall(communicate_socket, status_code)
            await loop.sock_sendall(communicate_socket, size)
            await loop.sock_sendall(communicate_socket, sendpath)



class Action():   #操作类，具体存放FTP服务器允许的操作
    async def put(self, workdir, filename, communicate_socket, data_socket):
        print("filename :".format(filename))
        print(type(filename))
        filename = os.path.basename(filename)
        print("filename1:{}".format(filename))
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

    async def get(self, workdir, filename, communicate_socket, data_socket):
        sent_data_size = 0
        print("workdir = {}".format(workdir))
        filesize = os.path.getsize(workdir+'/'+filename)
        communicate_socket.send(bytes(str(filesize), encoding="utf-8"))
        with open(workdir+'/'+filename, 'rb') as f:
            while filesize > sent_data_size:
                data = f.read(1024)
                sent_data_size += 1024
                data_socket.send(data)
        print("File Transfer Finish, status code=200")
        communicate_socket.send(b'200')

    async def lsdir(self, workdir, tempdir):
        dir_list = os.listdir(workdir)
        dirlist = ""
        for i in dir_list:
            print(i)
            dirlist += i+"\n"
        con_len = sys.getsizeof(dirlist)
        print("dirlist = {}".format(dirlist))
        #communicate_socket.send(b"400")    #ls成功状态码400
        status_code = "400||"
        #communicate_socket.send(bytes(str(con_len), encoding="utf-8"))   #发送传输内容大小
        data = status_code+str(con_len)+"||"+dirlist
        return data
        '''
        if (con_len % 1024) != 0 and (con_len / 1024) != 0:  # 进行大小判断，保证能够传完
            times = int(con_len/1024)
            print(times)
            with open(tempdir+'tmp.txt', "w") as f:
                f.write(dirlist)
            with open(tempdir+'tmp.txt', "rb") as f:
                for i in range(times + 1):
                    dir_list_div = f.read(1024)
                    communicate_socket.send(dir_list_div)
        else:
            communicate_socket.send(dir_list)
        '''

    async def mkdir(self, communicate_socket, cmd, workdir):
        cmd_split = cmd.split(" ")
        Directory = cmd_split[1]
        #communicate_socket.send(b"4")
        if os.path.exists(workdir+"/"+Directory):
            #communicate_socket.send(b"501")   #使用501状态码进行文件夹存在的状态码
            return b"501"
        else:
            os.makedirs(workdir+"/"+Directory)
            #communicate_socket.send(b"500")   #使用500状态码表示文件夹创建成功
            return b"500"

    async def pwd(self,  workpath):
        path = workpath
        print("path is {}".format(path))
        print(type(path))
        pathsize = sys.getsizeof(path)
        '''
        communicate_socket.send(b"600")   #pwd成功状态码
        communicate_socket.send(bytes(str(pathsize), encoding="utf-8"))
        communicate_socket.send(bytes(path, encoding="utf-8"))
        '''
        data = "600||"+str(pathsize)+"||"+path
        return data

    async def cd(self, cmd, topdir, workdir):
        cmd_split = cmd.split(" ")
        path = cmd_split[1]
        print(path)
        print(type(path))
        chdir = workdir+path+"/"
        print("workdir {}".format(workdir))
        print("chdir {}".format(chdir))
        chdir_path = os.path.dirname(chdir) + '/'
        print("chdir_path {}".format(chdir_path))
        print("topdir {}".format(topdir))
        if path == "/":  #跳转到共享的根目录,ok
                return "300 "+topdir
        elif path == "..":
                print("workdir:{}".format(workdir))
                upper_dir = os.path.dirname(workdir[:-1])
                print("upper_dir :{}".format(upper_dir))
                return "300 "+upper_dir
        elif path == ".": #跳转到当前目录,ok
                return "300 "+workdir
        elif os.path.exists(chdir):
            print(topdir in chdir_path)
            if (topdir in chdir_path) or (topdir == chdir_path):
                print("workdir:{}".format(workdir))
                if os.path.isdir(chdir):
                    return "300 "+chdir
                else:
                    return "303 "  #跳转到的不是文件夹，返回状态码303
            else:
                return "302 " #超过顶级目录的状态码
        else:
            return "301 "  ##当前工作目录中不存在此目录


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    c = Control()
    loop.run_forever()
