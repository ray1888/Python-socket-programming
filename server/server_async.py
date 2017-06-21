import asyncio
import socket
import re
import os


async def acceptd(sock):
    conn, addr = await loop.sock_accept(sock)  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    loop.create_task(read(conn))

def ls(connect_socket):
    dircontent = os.listdir('E:/FTP')
    data = ''
    for item in dircontent:
        data += item
    connect_socket.send(bytes(data, encoding="utf-8"))


async def read(connect_socket):
    cmd = connect_socket.recv(1024)  # Should be ready
    print(cmd)
    print(type(cmd))
    cmd = cmd.decode('ascii')
    print(cmd)
    print(type(cmd))
    if cmd == "ls":
        ls(connect_socket)
    if cmd == "quit":
        print('closing', connect_socket)
        connect_socket.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    sock = socket.socket()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost', 17773))
    sock.listen(100)
    sock.setblocking(False)
    while 1:
        loop.create_task(acceptd(sock))

    loop.run_forever()



