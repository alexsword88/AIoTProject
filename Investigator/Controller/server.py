import socket
import time
from configparser import ConfigParser

import requests
import serial

config = ConfigParser()
config.read("config.ini")
config = config["server"]

server = socket.socket()
server.bind((config["HOST"], config.getint("PORT")))
server.listen(5)


def handlerClient(client, robotCOM, robotBaudRate, wioCOM, wioBaudRate):
    with (serial.Serial(robotCOM, robotBaudRate, timeout=0) as robotSer,
          serial.Serial(wioCOM, wioBaudRate, timeout=0) as wioSer):
        time.sleep(2)  # wait arduino ready
        while True:
            try:
                data = client.recv(1)
                if data == b'm':
                    requests.get("http://127.0.0.1:54322/jobComplete")
                elif data != b'e':
                    if data != b'i':
                        robotSer.write(data)
                    else:
                        wioSer.write(data)
                else:
                    break
            except ConnectionResetError:
                return


print("[*] Ready to accept")
while True:
    client, address = server.accept()
    print("[*] Client Accepted")
    handlerClient(client, config["ROBOT_COM"], config["ROBOT_BAUD_RATE"],
                  config["WIO_COM"], config["WIO_BAUD_RATE"])
    print("[*] Client Closed")
    client.close()
