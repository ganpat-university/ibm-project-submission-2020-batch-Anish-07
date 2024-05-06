import cv2
import numpy as np
import dlib
from imutils import face_utils
from tensorflow.keras.models import load_model

# Load the face detector from dlib
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Load the liveness detection model
liveness_model = load_model("liveness_model.h5")

# Define the mapping of liveness labels
liveness_labels = {0: 'Fake', 1: 'Real'}

# Initialize the video capture
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = detector(gray)

    for face in faces:
        # Determine the facial landmarks for the face region
        shape = predictor(gray, face)
        shape = face_utils.shape_to_np(shape)

        # Extract the region of interest (ROI) for the face
        (x, y, w, h) = cv2.boundingRect(np.array([shape[48:68]]))
        face_roi = gray[y:y + h, x:x + w]
        face_roi = cv2.resize(face_roi, (32, 32))
        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_GRAY2BGR)
        face_roi = np.expand_dims(face_roi, axis=0)
        face_roi = face_roi / 255.0

        # Perform liveness prediction using the liveness detection model
        liveness_prediction = liveness_model.predict(face_roi)
        liveness_score = liveness_prediction[0][0]
        liveness_label = liveness_labels[int(liveness_score > 0.5)]

        # Draw the bounding box and liveness label on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, liveness_label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Liveness Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
video_capture.release()
cv2.destroyAllWindows()