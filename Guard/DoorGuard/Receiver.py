import radio
from microbit import *

radio.config(group=223, power=2)
radio.on()
uart.init(9600)

PLAY_PIN = pin1
RECORD_PIN = pin15
RECORD_PIN.set_pull(RECORD_PIN.NO_PULL)
PLAY_PIN.set_pull(PLAY_PIN.NO_PULL)
RECORD_PIN.write_digital(1)
PLAY_PIN.write_digital(1)


def recording():
    global RECORD_PIN
    RECORD_PIN.write_digital(0)
    sleep(5000)
    RECORD_PIN.write_digital(1)
    sleep(2000)


def play():
    global PLAY_PIN
    PLAY_PIN.write_digital(0)
    sleep(100)
    PLAY_PIN.write_digital(1)
    sleep(3000)


def readButton():
    buttonA = button_a.was_pressed()
    buttonB = button_b.was_pressed()
    if buttonA and buttonB:
        return 2
    elif buttonA:
        return 0
    elif buttonB:
        return 1
    else:
        return -1


def warning():
    count = 0
    while True:
        if count == 0:
            play()
        if readButton() == 1:
            resetWarning()
            break
        sleep(1000)
        count += 1
        if count > 3:
            count = 0


def resetWarning():
    while True:
        if readButton() == 1:
            break
        msg = radio.receive_bytes()
        if msg and msg == b'0':
            uart.write(b'5')
            while True:
                data = uart.read()
                if data and data == b'0':
                    break
            break
        radio.send_bytes(b'5')
        sleep(1000)


def warningReceive():
    target = 0
    sendTemp = 0
    while True:
        if sendTemp > 10:
            radio.send_bytes(b'2')
            radio.send("%.2f" % temperature())
            sendTemp = 0
        display.set_pixel(2, 2, target)
        event = radio.receive_bytes()
        if event and event == b'4':
            radio.send_bytes(b'0')
            uart.write(b'4')
            while True:
                data = uart.read()
                if data and data == b'0':
                    break
            break
        elif event and event == b'6':
            data = radio.receive_bytes()
            radio.send_bytes(b'0')
            uart.write(b'6')
            uart.write(data)
        sleep(500)
        sendTemp += 1
        target = 9 if target == 0 else 0
    display.scroll("Door Open", wait=False)


# recording()
while True:
    warningReceive()
    warning()
