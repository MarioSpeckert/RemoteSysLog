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
broadcast_ip = '172.16.0.255'

class Server():
    def __init__(self) -> None:
        self.sock_ping = None
        self.sock_server = None
        self.ping_port = 12345
        self.server_port = 12346

        self.server_thread = threading.Thread(target=self.receive_data)
        self.init_ping_socket()
        self.init_server_socket()
        self.running = True
        self.clients = []
        self.log_file = open('sysmon_log.txt', 'a')

    def init_ping_socket(self):
        self.sock_ping = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP) # UDP
        self.sock_ping.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.sock_ping.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        # Enable broadcasting mode
        self.sock_ping.bind(('', self.ping_port))

    def init_server_socket(self):
        self.sock_server = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.sock_server.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
        self.sock_server.bind(('', self.server_port))

    def get_ip_addr(self):
        ip = self.sock_ping.getsockname()[0]
        return ip

    def receive_data(self):
        while self.running:
            data, addr = self.sock_server.recvfrom(1024)
            data = data.decode('utf-8')
            if data == 'sysmon_pong':
                print('sysmon_pong')
                ip = addr[0]
                if ip not in self.clients:
                    print('new client')
                    self.clients.append(ip)
            if data[0] == '{':
                data = data.replace("'", '"')

                d = json.loads(data)
                d['addr'] = addr[0]
                self.log_file.write(json.dumps(d) + '\n')
                self.log_file.flush()


    def start(self) -> None:
        self.server_thread.start()
        self.send_ping()
        self.send_start()

    def stop(self) -> None:
        self.running = False
        self.sock_server.close()

    
    def joint_all(self):
        self.server_thread.join()
    
    def send_ping(self):
        print('sending ping')
        self.sock_ping.sendto(b'sysmon_ping', (broadcast_ip, self.ping_port))
    
    def send_start(self):
        print('sending start')
        self.send_to_known_clients(b'start')
    
    def send_stop(self):
        print('sending stop')
        self.send_to_known_clients(b'stop')

    def send_to_known_clients(self, data):
        for ip in self.clients:
            self.sock_server.sendto(data, (ip , self.server_port))

    def exit(self):
        self.log_file.close()
        self.sock_server.close()
        self.sock_ping.close()
        del self.server_thread
        print('press ctrl-c to exit')
        sys.exit(0)

def main():
    server = Server()
    server.start()
    while True:
        c = input('q to quit\n')
        if c == 'q':
            #close file and stop server
            server.exit()
        if c == 'x':
            server.send_stop()
    sys.exit(0)


if __name__ == "__main__":
    main()
