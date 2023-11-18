#!/bin/env python3

import sys
import os
import argparse
import subprocess

import time

from socket import *
import threading
import json

# adjust the broadcast ip to your network
broadcast_ip = '192.168.2.255'

class Server():
    def __init__(self) -> None:
        self.sock_ping = None
        self.sock_server = None
        self.ping_port = 12345
        self.server_port = 12348
        self.send_port = 12349

        self.server_thread = threading.Thread(target=self.receive_data)
        self.init_ping_socket()
        self.init_server_socket()
        self.running = True
        self.clients = []
        self.log_file = open('/home/mario/sysmon_log.txt', 'a')
        self.send_sockets = []

    def init_send_socket(self, ip):
        sock_send = socket(AF_INET, SOCK_STREAM)
        sock_send.connect((ip, self.send_port))
        self.send_sockets.append(sock_send)

    def init_ping_socket(self):
        self.sock_ping = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) # UDP
        self.sock_ping.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.sock_ping.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # Enable broadcasting mode
        self.sock_ping.bind(('', self.ping_port))

    def init_server_socket(self):
        self.sock_server = socket(AF_INET, SOCK_STREAM)
        self.sock_server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        self.sock_server.bind(('', self.server_port))
        self.sock_server.listen(10)

    def get_ip_addr(self):
        ip = self.sock_ping.getsockname()[0]
        return ip

    def receive_data(self):
        while True:
            print('waiting for connection')
            sock, addr = self.sock_server.accept()

            print('accepted connection')
            data = sock.recv(1024)
            data = data.decode('utf-8')
            print(data)
            if data == 'sysmon_pong':
                print('sysmon_pong')
                ip = addr[0]
                if ip not in self.clients:
                    print('new client')
                    self.clients.append(ip)
                    self.init_send_socket(ip)

            if data[0] == '{':
                data = data.replace("'", '"')

                d = json.loads(data)
                d['addr'] = addr[0]
                self.log_file.write(json.dumps(d) + '\n')
                self.log_file.flush()


    def startup(self) -> None:
        self.server_thread.start()
        self.send_ping()
        time.sleep(1)
        self.send_start()

    def stop(self) -> None:
        self.running = False
        self.sock_server.close()

    
    def join_all(self):
        self.server_thread.join()
    
    def send_ping(self):
        print('sending ping')
        self.sock_ping.sendto(b'sysmon_ping', (broadcast_ip, self.ping_port))

    def send_start(self):
        print('sending start')
        self.send_to_known_clients('start')
    
    def send_stop(self):
        print('sending stop')
        self.send_to_known_clients('stop')

    def send_to_known_clients(self, data):
        for sock in self.send_sockets:
            sock.sendall(data.encode())
    
    def list_clients(self):
        print(self.clients)

    def exit(self):
        self.log_file.close()
        self.sock_server.close()
        self.sock_ping.close()
        for sock in self.send_sockets:
            sock.close()
        del self.server_thread
        print('press ctrl-c to exit')
        sys.exit(0)

def main():
    server = Server()
    server.startup()
    while True:
        c = input('q to quit\n')
        if c == 'q':
            #close file and stop server
            server.exit()
        if c == 'x':
            server.send_stop()
        if c == 'l':
            server.list_clients()
        if c == 's':
            server.send_start()
        if c == 'p':
            server.send_ping()
    sys.exit(0)


if __name__ == "__main__":
    main()
