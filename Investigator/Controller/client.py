import socket
from configparser import ConfigParser

import keyboard

config = ConfigParser()
config.read("config.ini")
config = config["client"]
client = socket.socket()
client.connect((config["SERVER_IP"], config.getint("SERVER_PORT")))


def onDirectionClick(direction):
    global client
    client.send(direction)


keyboard.add_hotkey('up', onDirectionClick, (b'w',))
keyboard.add_hotkey('down', onDirectionClick, (b's',))
keyboard.add_hotkey('left', onDirectionClick, (b'a',))
keyboard.add_hotkey('right', onDirectionClick, (b'd',))
keyboard.add_hotkey('m', onDirectionClick, (b'm',))
keyboard.add_hotkey('enter', onDirectionClick, (b'i',))
keyboard.add_hotkey('space', onDirectionClick, (b'x',))

print("[*] Ready to send, press esc to exit")
keyboard.wait('esc')
client.send(b"e")
client.close()
