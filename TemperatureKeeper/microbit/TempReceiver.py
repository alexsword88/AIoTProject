import radio
from microbit import *

radio.config(group=223, power=2)
radio.on()
uart.init(9600)

while True:
    event = radio.receive_bytes()
    if event and event == b'2':
        data = radio.receive()
        if data is not None:
            uart.write(b'2')
            uart.write(data)
    sleep(500)
