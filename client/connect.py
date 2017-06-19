import socket

if __name__ == "__main__":
    sock = socket.socket()
    sock.connect(("127.0.0.1", 25699))
    while 1:
        data = input("please input sth \t")
        data = bytes(data, encoding="utf-8")
        sock.send(data)
        recv_data = sock.recv(2048)
        recv_data = recv_data.decode("ascii")
        print(recv_data)