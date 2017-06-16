import socket
import asyncio

def waiting(sock):
    sock.listen(5)
    sock_acc, addr = sock.accept()
    return sock_acc

async def sendhello(sendsock):
    sendsock.send(b'100')
    remote = sendsock.getsockname()
    print("{} is connect".format(remote[0]))

async def createsock():
    sock = socket.socket()
    sock.setblocking(0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 8999))
    sock_acc = waiting(sock)
    await sendhello(sock_acc)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    #task = [createsock() for i in range(5)]
    #loop.run_until_complete(task)
    task = [loop.create_task(createsock())]
    loop.run_until_complete(task)
    loop.close()
