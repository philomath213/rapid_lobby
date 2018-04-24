from core import *
import argparse


def run_client(server_host, server_port):
    def printRecvMsg(msg):
        """print the received messages"""
        print('\r'+msg+'\n>> ', end='')

    try:
        c = Client(server_host, server_port, printRecvMsg)
        print("[+] Connected To: %s:%s" % (server_host, str(server_port)))
    except socket.error as e:
        print("[-] Connection Error !!")
        exit(-1)
    try:
        username = input("username: ")
        print("[+] loggin ...")
        c.auth(username)
        c.recv_handler.start()
    except Exception as e:
        print("[-] Auth Error")
        exit(-2)
    while 1:
        try:
            buf = input(">> ")
            c.sendMsg(buf)
        except KeyboardInterrupt:
            print("\n[+] exiting client")
            c.stopClient()
        except ServerError as e:
            print('[-]', e.message, ', exiting client')
            exit(0)

def run_server(host, port, max_clients_num):
    s = Server(host, port, max_clients_num)
    s.startServer()

def main():
    arg_parser = argparse.ArgumentParser()
    subparsers = arg_parser.add_subparsers(dest='command')
    parser_create = subparsers.add_parser("create")
    parser_create.add_argument("host", help="host service address")
    parser_create.add_argument("port", type=int,
                            help="host service port")
    parser_create.add_argument("-m", "--max_clients_num", type=int, default=8,
                               help="max clients number")

    parser_join = subparsers.add_parser("join")
    parser_join.add_argument("host", help="host service address")
    parser_join.add_argument("port", type=int,
                            help="host service port")

    args = arg_parser.parse_args()
    if args.command == "create":
        run_server(args.host, args.port, args.max_clients_num)
    elif args.command == "join":
        run_client(args.host, args.port)


if __name__ == '__main__':
    main()
