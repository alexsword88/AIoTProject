import threading
import time
from configparser import ConfigParser

import eel
import serial

config = ConfigParser()
config.read("config.ini")
config = config["server"]
MAX_TEMP = 10
shutdown = False
temperature = []
triggerTemp = 0


def calcTemp():
    return "%.2f" % (sum(temperature) / len(temperature))


def addTemp(temp):
    if len(temperature) >= MAX_TEMP:
        temperature.pop(0)
    temperature.append(temp)


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
            if event == b'2':
                time.sleep(0.5)
                try:
                    addTemp(float(ser.readall().decode()))
                    eel.onTempUpdate(calcTemp())
                except ValueError:
                    pass
                ser.reset_output_buffer()
                ser.write(b'0')
            time.sleep(0.5)


def listenArduinoSerialEvent(com, baudRate):
    global shutdown, temperature
    with serial.Serial(com, baudRate, timeout=0) as ser:
        time.sleep(2)  # wait arduino ready
        while not shutdown:
            event = ''
            try:
                event = ser.read()
            except ValueError:
                time.sleep(0.5)
            if event == b'2':
                time.sleep(0.5)
                try:
                    addTemp(float(ser.readall().decode()))
                    eel.onTempUpdate(calcTemp())
                except ValueError:
                    pass
                ser.reset_output_buffer()
                ser.write(b'0')
            elif event == b'1':
                try:
                    triggerTemp = int(ser.readall().hex(), 16)
                    eel.onTriggerUpdate(triggerTemp)
                except ValueError:
                    pass
                ser.reset_output_buffer()
                ser.write(b'0')
            time.sleep(0.5)


def onShutDown(_, __):
    global shutdown
    shutdown = True


eel.init('web')
arduinoThread = threading.Thread(target=listenArduinoSerialEvent,
                                 args=(config["ARDUINO_COM"],
                                       config.getint("ARDUINO_BAUD_RATE")))
arduinoThread.start()
microbitThread = threading.Thread(target=listenMicrobitSerialEvent,
                                  args=(config["MICROBIT_COM"],
                                        config.getint("MICROBIT_BAUD_RATE")))
microbitThread.start()

eel.start('index.html',
          host=config["HOST_IP"],
          close_callback=onShutDown)
arduinoThread.join()
microbitThread.join()
