import socket

s = socket.socket()
port = 8101
s.bind(("127.0.0.1", port))
s.listen(5)

c, addr = s.accept()
print(type(c))
print(addr)
print(c)
##print('get connect from'+ addr)
c.send(b'You are already connect in server')

while True:
    rec_str = c.recv(1024)
    print(c)
    print('rec_str={}'.format(rec_str))
    if rec_str == b'quit' or rec_str == b'q':
        print("out")
        c.send(bytes('0',encoding="utf-8"))
        c.close()
        break
    else:
        c.send(bytes('try another cmd ,it not dead', encoding="utf-8"))