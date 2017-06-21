import socket
import os
import re

if __name__ == "__main__":
    sock = socket.socket()
    sock.connect(("127.0.0.1", 17773))
    while 1:
        cmd = input("please input sth \t")
        split_cmd = cmd.split(" ")
        filename = split_cmd[1]
        action = split_cmd[0]
        cmd = bytes(cmd, encoding="utf-8")
        sock.send(cmd)
        if re.match('put', action):
            remoteport = sock.recv(2048)
            remoteport = remoteport.decode("ascii")
            remoteport = int(remoteport)
            new_sock = socket.socket()
            new_sock.connect(('127.0.0.1', remoteport))
            status = sock.recv(1024)
            print(status)
            filensize = os.path.getsize(filename)
            filensize_byte = bytes(str(filensize), encoding="utf-8")
            sock.send(filensize_byte)
            print("filensize {}".format(filensize))
            send_size = 0
            while filensize > send_size:
                with open(filename, 'rb') as f:
                    data = f.read(1024)
                    new_sock.send(data)
                    send_size += 1024
            new_sock.close()
        else:
            remoteport = sock.recv(2048)
            remoteport = remoteport.decode("ascii")
            remoteport = int(remoteport)
            new_sock = socket.socket()
            new_sock.connect(('127.0.0.1', remoteport))
            status_code = sock.recv(1024)
            print(status_code)
            filesize = sock.recv(1024)
            filesize = int(filesize)
            recv_size = 0
            cwd = os.getcwd()
            with open(cwd+"/"+filename, 'wb') as f:
                while filesize>recv_size:
                    data = new_sock.recv(1024)
                    f.write(data)
                    recv_size += 1024




