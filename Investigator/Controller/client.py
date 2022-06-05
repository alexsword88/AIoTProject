import socket
from configparser import ConfigParser

import keyboard
import pyjoystick
from pyjoystick.sdl2 import Joystick, Key, run_event_loop

config = ConfigParser()
config.read("config.ini")
config = config["client"]
client = socket.socket()
client.connect((config["SERVER_IP"], config.getint("SERVER_PORT")))


def onDirectionClick(direction):
    global client
    client.send(direction)


def handle_key_event(key):
    if key.keyname == "Button 8":
        client.send(b'x')
    if key.value == Key.HAT_UP:
        client.send(b'w')
    elif key.value == Key.HAT_DOWN:
        client.send(b's')
    elif key.value == Key.HAT_LEFT:
        client.send(b'a')
    elif key.value == Key.HAT_RIGHT:
        client.send(b'd')


keyboard.add_hotkey('up', onDirectionClick, (b'w',))
keyboard.add_hotkey('down', onDirectionClick, (b's',))
keyboard.add_hotkey('left', onDirectionClick, (b'a',))
keyboard.add_hotkey('right', onDirectionClick, (b'd',))
keyboard.add_hotkey('m', onDirectionClick, (b'm',))
keyboard.add_hotkey('enter', onDirectionClick, (b'i',))
keyboard.add_hotkey('space', onDirectionClick, (b'x',))
repeater = pyjoystick.HatRepeater(first_repeat_timeout=0.5,
                                  repeat_timeout=0.5,
                                  check_timeout=0.5)
mngr = pyjoystick.ThreadEventManager(event_loop=run_event_loop,
                                     handle_key_event=handle_key_event,
                                     button_repeater=repeater)
mngr.start()

print("[*] Ready to send, press esc to exit")
keyboard.wait('esc')
client.send(b"e")
client.close()
