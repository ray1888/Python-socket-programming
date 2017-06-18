import selectors
import socket
import re
import os

sel = selectors.DefaultSelector()

def accept(sock):
    conn, addr = sock.accept()  # Should be ready
    print('accepted', conn, 'from', addr)
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)
    event1 = sel.select()
    for item1,mask1 in event1:
        print("item1 {}".format(item1))
        print("mask1 {}".format(mask1))

def ls(conn):
    dircontent = os.listdir('E:/FTP')
    data = ''
    for item in dircontent:
        data += item
    conn.send(bytes(data, encoding="utf-8"))
    #sel.unregister(conn)
    event2 = sel.select()
    for item2,mask2 in event2:
        print("item2 {}".format(item2))
        print("mask2 {}".format(mask2))

    sel.modify(conn, selectors.EVENT_READ, read)

def read(conn):
    cmd = conn.recv(1024)  # Should be ready
    print(cmd)
    print(type(cmd))
    cmd = cmd.decode('ascii')
    print(cmd)
    print(type(cmd))
    if cmd == "ls":
        #sel.unregister(conn)
        sel.modify(conn, selectors.EVENT_WRITE, ls)


    if cmd == "quit":
        sel.unregister(conn)
        print('closing', conn)
        conn.close()

sock = socket.socket()
sock.bind(('localhost', 17773))
sock.listen(100)
sock.setblocking(False)
sel.register(sock, selectors.EVENT_READ, accept)


while True:
    events = sel.select()
    print(events)
    for item in events:
        print("item is {} \n".format(item))
    for key, mask in events:
        callback = key.data
        print("callback is {}".format(callback))
        #callback(key.fileobj, mask)
        callback(key.fileobj)