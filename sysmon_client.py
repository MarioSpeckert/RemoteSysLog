#!/bin/env python3

import sys
import os
import argparse
import subprocess

import psutil
import time
import datetime

from socket import *
import threading

# adjust the interval to your needs
interval = 60 # seconds
class SysPerfMonitor:

    def __init__(self) -> None:
        pass

    def get_cpu_usage(self):
        cpu_usage = psutil.cpu_percent(interval=0.1, percpu=True)
        return cpu_usage

    def get_mem_usage(self):
        mem_usage = psutil.virtual_memory().percent
        return mem_usage

    def get_disk_usage(self):
        disk_usage = psutil.disk_usage('/').percent
        return disk_usage

    def get_core_temp(self):
        temps = []
        cpu_temps = psutil.sensors_temperatures()['cpu_thermal']
        for cpu_temp in cpu_temps:
            temps.append(cpu_temp.current)
        #cpu_temp = psutil.sensors_temperatures()['coretemp'][0].current

        return temps

class Server():
    def __init__(self) -> None:
        self.perf_monitor = SysPerfMonitor()
        self.ip_addr = None
        self.sock_ping = None
        self.sock_server = None
        self.running = False
        self.ping_port = 12345
        self.server_port = 12346
        self.server_addr = None

        self.init_ping_socket()
        self.init_server_socket()
        self.ping_thread = threading.Thread(target=self.receive_ping)
        self.server_thread = threading.Thread(target=self.server)
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

    def receive_ping(self):
        while True:
            data, addr = self.sock_ping.recvfrom(1024)
            if data.decode() == 'sysmon_ping':
                data = 'sysmon_pong'
                self.server_addr = addr[0]
                self.sock_server.sendto(data.encode(), (addr[0], self.server_port))

    def server(self):
        while True:
            data, addr = self.sock_server.recvfrom(1024)
            data = data.decode()
            if data == 'start':
                self.running = True
                self.start_monitor()
            if data == 'stop':
                self.running = False

    def start(self) -> None:
        self.ping_thread.start()
        self.server_thread.start()

    def receive(self):
        data, addr = self.sock_ping.recvfrom(1024)
        print(data.decode())
        print(addr)

    def start_monitor(self):
        while self.running:
            data = {}
            data["cpu_usage"] = self.perf_monitor.get_cpu_usage()
            data["mem_usage"] = self.perf_monitor.get_mem_usage()
            data["disk_usage"] = self.perf_monitor.get_disk_usage()
            data["core_temp"] = self.perf_monitor.get_core_temp()
            data['time'] = str(datetime.datetime.now())
            self.sock_server.sendto(str(data).encode(), (self.server_addr, self.server_port))
            self.log_file.write(str(data) + '\n')
            self.log_file.flush()
            time.sleep(interval)

    def stop(self):
        self.running = False

    def joint_all(self):
        self.ping_thread.join()
        self.server_thread.join()

def main():
    server = Server()
    server.init_ping_socket()
    server.start()

if __name__ == "__main__":
    main()
