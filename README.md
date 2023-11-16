# RemoteSysLog
## Brief
This is a simple remote system monitoring tool. It consists of a server and a client. The server can ping the clients and start the monitoring. The client will send the system information to the server. The server will store the information in a logfile.
## Disclaimer
There will be no guarantee for the functionality of this software. Use at your own risk!
## Usage
### Client
* start the client with `python3 sysmon_client.py`

### Server
* start the server with `python3 sysmon_server.py`
* press 'p' and 'enter' to ping the clients
* press 's' and 'enter' to start the client monitoring
* ctrl+c twice to stop the server

### Logfile
* data is stored in `sysmon_log.txt` in the same directory as the server was started

### Known Issues
* stopping the client and server is not working
* quitting the client and server is not working
