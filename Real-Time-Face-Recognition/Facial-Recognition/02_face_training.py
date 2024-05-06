import cv2
import numpy as np
from PIL import Image
import os

# Path for face image database
path = "Facial-Recognition/dataset"

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# function to get the images and label data
def getImagesAndLabels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]     
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        # Load image
        img = cv2.imread(imagePath)

        # Convert to grayscale if 3D image
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img

        # Detect faces
        faces = detector.detectMultiScale(gray)

        for (x, y, w, h) in faces:
            faceSamples.append(gray[y:y+h, x:x+w])
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            ids.append(id)

    return faceSamples, ids

print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
faces, ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))

# Save the model into trainer/trainer.yml
recognizer.write("Facial-Recognition/trainer/trainer.yml")
print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
