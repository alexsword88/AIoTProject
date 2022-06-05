# Imports go at the top
import radio
from microbit import *

radio.config(group=223, power=7)
radio.on()

lastState = None
minState = 9999999
maxState = 0

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

def waitStart():
    global lastState
    display.show(Image.TARGET)
    while True:
        if readButton() == 0:
            lastState = compass.get_field_strength()
            break
        sleep(500)

def sampling():
    global minState,maxState
    minState = 9999999
    maxState = 0
    y = 0
    x = 0
    display.show(Image('99999:'
                       '99999:'
                       '99999:'
                       '99999:'
                       '99999'))
    for i in range(25):
        stateNow = compass.get_field_strength()
        if minState > stateNow:
            minState = stateNow
        if maxState < stateNow:
            maxState = stateNow
        display.set_pixel(x,y,0)
        x+=1
        if x > 4:
            y += 1
            x = 0
        sleep(400)
    display.show(Image.YES)
    sleep(1000)
    minState = int(minState * 0.95)
    maxState = int(maxState * 1.05)

def detecting():
    global minState,maxState
    display.clear()
    print(minState, maxState)
    count = 0
    target = False
    while True:
        if count % 10 == 0:
            display.set_pixel(2,2, target)
            target = not target
        stateNow = compass.get_field_strength()
        print(stateNow)
        if stateNow > maxState or stateNow < minState:
            break
        sleep(500)
        count+=1
        
    display.show(Image.NO)
    sleep(400)

def warning():
    while True:
        radio.send_bytes(b'4')
        ack = radio.receive_bytes()
        if ack and ack == b'0':
            break
        sleep(1000)
    sleep(1000)

def waitReset():
    while True:
        event = radio.receive_bytes()
        if event and event == b'5':
            radio.send_bytes(b'0')
            break
        if readButton() == 1:
            break
        sleep(500)
    display.scroll("Reset")
    sleep(1000)

    
while True:
    if compass.is_calibrated():
        break
    compass.calibrate()

waitStart()
while True:
    sampling()
    detecting()
    warning()
    waitReset()
