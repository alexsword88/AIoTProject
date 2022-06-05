import pickle
import socket
import time
from configparser import ConfigParser

import face_recognition
from flask import Flask, request
from werkzeug.utils import secure_filename

config = ConfigParser()
config.read("config.ini")
config = config["server"]
app = Flask(__name__)
SAVE_PATH = "web/target.jpg"
with open("faceModel.pkl", "rb") as model:
    faceModel = pickle.load(model)


@app.route("/person", methods=['POST'])
def foundPerson():
    global faceModel
    file = request.files['file']
    file.save(SAVE_PATH)
    image = face_recognition.load_image_file(file)
    faceLocation = face_recognition.face_locations(image)
    if len(faceLocation) > 0:
        test_image_enc = face_recognition.face_encodings(image)
        closest_distances = faceModel.kneighbors(test_image_enc, n_neighbors=1)
        are_matches = [closest_distances[0][i][0] <= 0.4
                       for i in range(len(faceLocation))]
        name = [(pred, loc) if rec else ("未知", loc)
                for pred, loc, rec in zip(faceModel.predict(test_image_enc),
                                          faceLocation, are_matches)]
        name = name[0]
        client = socket.socket()
        client.connect(("127.0.0.1", config.getint("PORT")))
        client.send(b'7')
        client.send(str(name[0]).encode("utf-8"))
        time.sleep(0.5)
        client.close()
        return "OK"
    else:
        return "NG"


if __name__ == "__main__":
    app.run(host=config["HOST_IP"], port=config.getint("PORT"))
