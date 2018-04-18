import socket
import threading

PORT = 2130
HOST = '127.0.0.1'
BUFFER_SIZE = 1024

class Client():
    class RecvHandler(threading.Thread):
        def __init__(self, attached_client, msg_handler):
            threading.Thread.__init__(self)
            self.attached_client = attached_client
            # Event to terminate the thread
            self._stopevent = threading.Event()
            self.msg_handler = msg_handler

        def run(self):
            "recv msgs"
            while not self._stopevent.isSet():
                buf = self.attached_client.socket.recv(BUFFER_SIZE).decode()
                if buf:
                    self.msg_handler(buf)
                else:
                    self.attached_client.stopClient()

        def join(self):
            """Stop the thread and wait for it to end"""
            # set the stop event then call the original join method
            self._stopevent.set()
            threading.Thread.join(self)


    def __init__(self, msg_handler):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_handler = self.RecvHandler(self, msg_handler)
        self.username = None

    def connect(self, host ,port):
        self.socket.connect((host, port))

    def auth(self, username):
        self.username = username
        self.socket.send(username.encode())

    def sendMsg(self, msg):
        self.socket.send(msg.encode())

    def stopClient(self):
        """shutdown the socket in order to unblock the recv_handler thread"""
        self.socket.shutdown(2)
        self.recv_handler.join()
        self.socket.close()
        exit(0)

def printRecvMsg(msg):
    """print the received messages"""
    print('\r'+msg+'\n>> ', end='')

def main():
    c = Client(printRecvMsg)
    try:
        c.connect(HOST, 1234)
        print("[+] Connected To: %s:%s" % (str(HOST), str(PORT)))
    except socket.error:
        print("[-] Connection problem !!")
        exit(-1)
    while 1:
        try:
            username = input("username: ")
            print("[+] loggin ...")
            c.auth(username)
            c.recv_handler.start()
            buf = input(">> ")
            c.sendMsg(buf)
        except KeyboardInterrupt:
            print("\n[+] exiting client")
            c.stopClient()


if __name__ == '__main__':
    main()
