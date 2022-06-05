import math
import os
import pickle

import face_recognition
from sklearn import neighbors

"""
Trains a k-nearest neighbors classifier for face recognition.
:param train_dir: directory that contains a sub-directory for each known person, with its name.
    (View in source code to see train_dir example tree structure)
    Structure:
    <train_dir>/
    ├── <person1>/
    │   ├── <somename1>.jpeg
    │   ├── <somename2>.jpeg
    │   ├── ...
    ├── <person2>/
    │   ├── <somename1>.jpeg
    │   └── <somename2>.jpeg
    └── ...
:param model_save_path: (optional) path to save model on disk
:param n_neighbors: (optional) number of neighbors to weigh in classification. Chosen automatically if not specified
:param knn_algo: (optional) underlying data structure to support knn.default is ball_tree
:param verbose: verbosity of training
:return: returns knn classifier that was trained on the given data.
"""
train_dir = "train_dir"
model_save_path = "faceModel.pkl"
distance_threshold = 0.4
n_neighbors = 3
X = []
y = []

# Loop through each person in the training set
for class_dir in os.listdir(train_dir):
    if not os.path.isdir(os.path.join(train_dir, class_dir)):
        continue

    # Loop through each training image for the current person
    for img_path in os.listdir(os.path.join(train_dir, class_dir)):
        img_path = os.path.join(train_dir, class_dir, img_path)
        image = face_recognition.load_image_file(img_path)
        face_bounding_boxes = face_recognition.face_locations(image)

        if len(face_bounding_boxes) != 1:
            print("Image {} not suitable for training: {}".format(
                img_path,
                "Didn't find a face"
                if len(face_bounding_boxes) < 1
                else "Found more than one face"))
        else:
            # Add face encoding for current image to the training set
            X.append(face_recognition.face_encodings(
                image,
                known_face_locations=face_bounding_boxes)[0])
            y.append(class_dir)

# Determine how many neighbors to use for weighting in the KNN classifier
if n_neighbors is None:
    n_neighbors = int(round(math.sqrt(len(X))))
    print("Chose n_neighbors automatically:", n_neighbors)

# Create and train the KNN classifier
knn_clf = neighbors.KNeighborsClassifier(
    n_neighbors=n_neighbors, algorithm='ball_tree', weights='distance')
knn_clf.fit(X, y)

# Save the trained KNN classifier
if model_save_path is not None:
    with open(model_save_path, 'wb') as f:
        pickle.dump(knn_clf, f)

# Load the test image with unknown faces into a numpy array
test_image = face_recognition.load_image_file('target.jpg')

# Find all the faces in the test image using the default HOG-based model
face_locations = face_recognition.face_locations(test_image)
no = len(face_locations)
print("Number of faces detected: ", no)

# Predict all the faces in the test image using the trained classifier
print("Found:")
test_image_enc = face_recognition.face_encodings(test_image)
closest_distances = knn_clf.kneighbors(test_image_enc, n_neighbors=1)
are_matches = [closest_distances[0][i][0] <= distance_threshold
               for i in range(len(face_locations))]
result = [(pred, loc) if rec else ("unknown", loc)
          for pred, loc, rec in zip(knn_clf.predict(test_image_enc),
                                    face_locations, are_matches)]
print(result)

with open("faceModel.pkl", "wb") as saveFile:
    pickle.dump(knn_clf, saveFile)
