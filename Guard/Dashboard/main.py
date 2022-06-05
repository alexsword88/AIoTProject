import socket
import threading
import time
from configparser import ConfigParser

import eel
import requests
import serial

shutdown = False
count = 0
config = ConfigParser()
config.read("config.ini")
config = config["server"]

server = socket.socket()
server.bind(("127.0.0.1", config.getint("PORT")))
server.listen(5)


INVESTIGATE_ROBOT_IP = config["INVESTIGATE_ROBOT_IP"]
INVESTIGATE_ROBOT_PORT = config["INVESTIGATE_ROBOT_PORT"]
robotTriggerURL =  \
    f"http://{INVESTIGATE_ROBOT_IP}:{INVESTIGATE_ROBOT_PORT}/checkDoor"


def onShutDown(path, websocketList):
    global shutdown, server
    server.close()
    shutdown = True

def listenSearchEvent():
    global server, shutdown
    while not shutdown:
        client, _ = server.accept()
        data = client.recv(1)
        if data == b'7':
            time.sleep(0.5)
            name = client.recv(1024)
            name = name.decode().strip()
            print(name)
            eel.onFaceFound(name)
        client.close()

def listenMicrobitSerialEvent(com, baudRate):
    global shutdown, temperature
    with serial.Serial(com, baudRate, timeout=0) as ser:
        time.sleep(2)  # wait microbit ready
        while not shutdown:
            event = ''
            try:
                event = ser.read()
            except ValueError:
                time.sleep(0.5)
            if event == b'4':
                try:
                    eel.onWarningTrigger()
                    requests.get(robotTriggerURL)
                except ValueError:
                    pass
                ser.reset_output_buffer()
                ser.write(b'0')
            elif event == b'5':
                try:
                    eel.onWarningReset()
                except ValueError:
                    pass
                ser.reset_output_buffer()
                ser.write(b'0')
            elif event == b'6':
                time.sleep(0.5)
                try:
                    eel.onTemperatureUpdate(float(ser.readall().decode()))
                except ValueError:
                    pass
                ser.reset_output_buffer()
            time.sleep(0.5)

eel.init('web')

microbitThread = threading.Thread(target=listenMicrobitSerialEvent,
                                  args=(config["MICROBIT_COM"],
                                        config.getint("MICROBIT_BAUD_RATE")))
microbitThread.start()
searchThread = threading.Thread(target=listenSearchEvent)
searchThread.start()
eel.start('index.html', close_callback=onShutDown)
