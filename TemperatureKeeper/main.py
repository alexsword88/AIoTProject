import threading
import time
from configparser import ConfigParser

import eel
import requests
import serial

config = ConfigParser()
config.read("config.ini")
config = config["server"]
MAX_TEMP = 10
shutdown = False
temperature = []
triggerTemp = 255
checkReady = True
checkRobotState = False
INVESTIGATE_ROBOT_IP = config["INVESTIGATE_ROBOT_IP"]
INVESTIGATE_ROBOT_PORT = config["INVESTIGATE_ROBOT_PORT"]
robotTriggerURL =  \
    f"http://{INVESTIGATE_ROBOT_IP}:{INVESTIGATE_ROBOT_PORT}/openAir"
robotStateURL =  \
    f"http://{INVESTIGATE_ROBOT_IP}:{INVESTIGATE_ROBOT_PORT}/state"


def checkReset():
    global checkReady
    checkReady = True


def calcTemp():
    global triggerOn, triggerTemp, checkRobotState, checkReady
    result = sum(temperature) / len(temperature)
    if checkRobotState:
        res = requests.get(robotStateURL)
        if res.text == "OK":
            checkRobotState = False
            eel.onTriggerOff()
    if checkReady:
        if result > triggerTemp:
            requests.get(robotTriggerURL)
            checkReady = False
            checkRobotState = True
            eel.onTriggerRaise()
            t = threading.Timer(1800, checkReset)
            t.start()
    return "%.2f" % result


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
    global shutdown, temperature, triggerOn, triggerTemp
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
