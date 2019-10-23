import socket
import threading
from queue import Queue

BUFFER_SIZE = 1024


class Server(object):
    def __init__(self, host, port, max_clients_num):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(max_clients_num)
        self.clients = dict()
        self.pending_messages = Queue()
        self.messages_handler = MessagesHandler(self)

    def startServer(self):
        self.messages_handler.start()
        print("[+] server started")
        while 1:
            try:
                client, addr = self.socket.accept()
                host, port = addr
                print('[+] New Connection from: %s:%s' % (host, port))
                client_th = ClientHandler(self, client)
                client_th.start()
            except KeyboardInterrupt:
                self.stopServer()

    def addMsgToQueue(self, sender, msg):
        "add message to pending_messages queue"
        self.pending_messages.put((sender, msg))

    def broadcastMsg(self, sender, msg):
        "send the msg to everyone"
        for c in self.clients:
            if c != sender:
                buf = "[%s]: %s" % (sender, msg)
                self.clients[c].sendMsg(buf)

    def addClient(self, username, client):
        self.clients[username] = client

    def removeClient(self, username):
        self.clients.pop(username)

    def stopServer(self):
        print("\n[+] exiting server")
        # terminate messages_handler thread
        self.messages_handler.join()
        # close clients sockets and terminate threads
        clients_handlers = set(self.clients.values())
        for c in clients_handlers:
            c.socket.shutdown(2)
            c.join()
            c.socket.close()

        self.socket.close()
        exit(0)


class MessagesHandler(threading.Thread):
    def __init__(self, attached_server):
        threading.Thread.__init__(self)
        self.attached_server = attached_server
        # Event to terminate the thread from the main thread
        self._stopevent = threading.Event()

    def run(self):
        "handle the pending_messages"
        while not self._stopevent.isSet():
            # Queue.get() is a blocking function
            sender, msg = self.attached_server.pending_messages.get()
            # TODO: add unicast and multicast functionality
            print('[%s]: %s' % (sender, msg))
            self.attached_server.broadcastMsg(sender, msg)

    def join(self):
        """Stop the thread and wait for it to end"""
        self._stopevent.set()
        # broadcast server stopping msg and unblock queue.get()
        self.attached_server.addMsgToQueue("admin", "Server shutdown !!")
        threading.Thread.join(self)


class ClientHandler(threading.Thread):
    def __init__(self, attached_server, client_socket):
        threading.Thread.__init__(self)
        self.attached_server = attached_server
        self.socket = client_socket
        self.host, self.port = client_socket.getpeername()
        self.username = None
        # Event to terminate the thread from the main thread
        self._stopevent = threading.Event()

    def run(self):
        # TODO: add auth functionality
        self.username = self.socket.recv(BUFFER_SIZE).decode()
        self.attached_server.addClient(self.username, self)
        while not self._stopevent.isSet():
            buf = self.socket.recv(BUFFER_SIZE).decode()
            if buf:
                self.attached_server.addMsgToQueue(self.username, buf)
            else:
                self.stop()
                return

    def sendMsg(self, msg):
        self.socket.send(msg.encode())

    def stop(self):
        self.attached_server.removeClient(self.username)

    def join(self):
        """Stop the thread and wait for it to end"""
        self._stopevent.set()
        threading.Thread.join(self)


class Client():
    def __init__(self, server_host, server_port, msg_handler):
        self.recv_handler = RecvHandler(self, msg_handler)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_host, server_port))
        self.username = None

    def auth(self, username):
        self.username = username
        self.socket.send(username.encode())

    def sendMsg(self, msg):
        try:
            self.socket.send(msg.encode())
        except Exception:
            raise ServerError("Server isn't running")

    def stopClient(self):
        """shutdown the socket in order to unblock the recv_handler thread"""
        self.socket.shutdown(2)
        self.recv_handler.join()
        self.socket.close()
        exit(0)


class ServerError(Exception):
    def __init__(self, message):
        self.message = message


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
            elif self._stopevent.isSet():
                return
            else:
                self.attached_client.stopClient()
                return

    def join(self):
        """set the stop event and wait for the thread to stop"""
        # set the stop event then call the original join method
        self._stopevent.set()
        # threading.Thread.join(self)
