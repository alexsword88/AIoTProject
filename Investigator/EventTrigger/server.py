import threading
from configparser import ConfigParser

import cv2
import numpy as np
import requests
import tflite_runtime.interpreter as tflite
from flask import Flask, Response, request

config = ConfigParser()
config.read("config.ini")
config = config["server"]

CAMERA_ID = 0
MODEL_PATH = "efficientdet_lite0.tflite"
NUM_THREADS = 4
WIDTH = 640
HEIGHT = 480
SCORE_THRESHOLD = 0.5
PERSON_CLASS = 0
SKIP_FRAME = 10
JOB_PROCESSING = False
guardURL = f"http://{config['GUARD_IP']}:{config['GUARD_PORT']}/person"
serachThread = None
app = Flask(__name__)


def personSearch():
    global serachThread
    # Add Robot Control
    cap = cv2.VideoCapture(CAMERA_ID)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    interpreter = tflite.Interpreter(model_path=MODEL_PATH,
                                     num_threads=NUM_THREADS)
    interpreter.allocate_tensors()
    inputDetails = interpreter.get_input_details()
    outputDetails = interpreter.get_output_details()
    MODEL_HEIGHT = inputDetails[0]['shape'][1]
    MODEL_WIDTH = inputDetails[0]['shape'][2]

    skipCount = 0
    saveCount = 0
    while cap.isOpened():
        success, image = cap.read()
        if skipCount < SKIP_FRAME:
            skipCount += 1
            continue
        skipCount = 0
        if not success:
            break
        oriImage = cv2.flip(image, 1)
        # oriImage = cv2.cvtColor(oriImage, cv2.COLOR_BGR2RGB)
        targetImage = cv2.resize(oriImage, (MODEL_HEIGHT, MODEL_WIDTH))
        inputData = np.expand_dims(targetImage, axis=0)
        interpreter.set_tensor(inputDetails[0]['index'], inputData)
        interpreter.invoke()

        detectBox = np.squeeze(
            interpreter.get_tensor(outputDetails[0]['index']))
        detectClass = np.squeeze(
            interpreter.get_tensor(outputDetails[1]['index']))
        detectScores = np.squeeze(
            interpreter.get_tensor(outputDetails[2]['index']))
        detectNum = np.squeeze(
            interpreter.get_tensor(outputDetails[3]['index']))

        maxIdx = -1
        lastScore = 0
        for i in range(int(detectNum)):
            if int(detectClass[i]) == PERSON_CLASS and  \
                    detectScores[i] > SCORE_THRESHOLD and \
                    detectScores[i] > lastScore:
                maxIdx = i

        if maxIdx != -1:
            try:
                ymin, xmin, ymax, xmax = detectBox[maxIdx]
                oriHeight, oriWidth, _ = oriImage.shape
                (left, right, top, bottom) = (xmin * oriWidth,
                                              xmax * oriWidth,
                                              ymin * oriHeight,
                                              ymax * oriHeight)
                y = int(top if top > 0 else 0)
                height = int(bottom - top)
                x = int(left if left > 0 else 0)
                width = int(right - left)
                crop = oriImage[y:y+height, x:x+width]
                _, buffer = cv2.imencode(".jpg", crop)
                cv2.imwrite(f'./original/{saveCount}.jpg', oriImage)

                files = {
                    "file": ('images.jpg', buffer)
                }
                res = requests.post(guardURL, files=files)
                if res.text == "OK":
                    break
            except:
                pass
        interpreter.reset_all_variables()
    serachThread = None


@app.route("/openAir", methods=['GET'])
def openAirCondition():
    global JOB_PROCESSING
    # Control Robot to Open Air Condition
    if not JOB_PROCESSING:
        JOB_PROCESSING = True
    return "OK"


@app.route("/jobComplete", methods=['GET'])
def jobComplete():
    global JOB_PROCESSING
    JOB_PROCESSING = False
    return "OK"


@app.route("/state", methods=['GET'])
def checkIsOpenAir():
    global JOB_PROCESSING
    return "NG" if JOB_PROCESSING else "OK"


@app.route("/checkDoor", methods=['GET'])
def checkDoorOpen():
    global serachThread
    if serachThread is None:
        serachThread = threading.Thread(target=personSearch)
        serachThread.start()
    return "OK"


if __name__ == "__main__":
    app.run(host=config["HOST"], port=config.getint("PORT"))
