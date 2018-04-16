import socket
import threading

PORT = 2130
HOST = '127.0.0.1'
BUFFER_SIZE = 1024

class Client():
    class RecvHandler(threading.Thread):
        def __init__(self, attached_client):
            threading.Thread.__init__(self)
            self.attached_client = attached_client
            # Event to terminate the thread from the main thread
            self._stopevent = threading.Event()

        def run(self):
            "recv msgs"
            while not self._stopevent.isSet():
                buf = self.attached_client.socket.recv(BUFFER_SIZE).decode()
                if buf:
                    print('\r'+buf+'\n>> ', end='')
                else:
                    self.attached_client.stopClient()

        def join(self):
            """Stop the thread and wait for it to end"""
            self._stopevent.set()
            threading.Thread.join(self)


    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_handler = self.RecvHandler(self)
        self.username = None

    def connect(self, host ,port):
        self.socket.connect((host, port))
        print("[+] Connected To: %s:%s" % (str(HOST), str(port)))

    def auth(self, username):
        self.username = username
        self.socket.send(username.encode())

    def startClient(self):
        self.recv_handler.start()
        while 1:
            try:
                buf = input(">> ")
                self.socket.send(buf.encode())
            except KeyboardInterrupt:
                self.stopClient()

    def stopClient(self):
        print("\n[+] exiting client")
        # shutdown the socket in order to unblock the recv_handler thread
        self.socket.shutdown(2)
        self.recv_handler.join()
        self.socket.close()
        exit(0)


def main():
    c = Client()
    c.connect(HOST, PORT)
    username = input("username: ")
    c.auth(username)
    c.startClient()


if __name__ == '__main__':
    main()
