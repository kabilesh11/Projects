import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime, timedelta
import face_recognition

# Path of the image folder 
path = 'D:\Projects\Facial Attendance Mini Project Expo\image_folder'

# IP address of ESP32-CAM
url = 'http://192.168.137.131/cam-hi.jpg'

# Initialize CSV file if it doesn't exist
if not os.path.isfile("Attendance.csv"):
    df = pd.DataFrame(columns=["Name", "Time"])
    df.to_csv("Attendance.csv", index=False)

# Read the image files 
images = []
classNames = []
myList = os.listdir(path)
print("Images found:", myList)

for cl in myList:
    if cl.lower().endswith(('png', 'jpg', 'jpeg')):  # Only process image files
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])

print("Class names:", classNames)

# Encode faces
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except IndexError:
            print(f"Face not detected in {img}")
    return encodeList

# Mark attendance with a 5-minute interval check
def markAttendance(name):
    df = pd.read_csv("Attendance.csv")

    now = datetime.now()
    dtString = now.strftime('%H:%M:%S')

    if name in df['Name'].values:
        # Get the last recorded time for the person
        last_entry_time_str = df.loc[df['Name'] == name, 'Time'].values[-1]
        last_time = datetime.strptime(last_entry_time_str, '%H:%M:%S')

        # If 5 minutes (300 seconds) have passed since last entry, update the attendance
        if (now - now.replace(hour=last_time.hour, minute=last_time.minute, second=last_time.second)) >= timedelta(minutes=5):
            new_entry = pd.DataFrame([[name, dtString]], columns=["Name", "Time"])
            df = pd.concat([df, new_entry], ignore_index=True)
            df.to_csv("Attendance.csv", index=False)
            print(f"Attendance marked for {name} at {dtString}")
    else:
        # First-time entry
        new_entry = pd.DataFrame([[name, dtString]], columns=["Name", "Time"])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv("Attendance.csv", index=False)
        print(f"Attendance marked for {name} at {dtString}")

# Get encodings of known faces
encodeListKnown = findEncodings(images)
print('Encoding Complete')

# Capture video from ESP32-CAM
while True:
    try:
        img_resp = urllib.request.urlopen(url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgnp, -1)
    except Exception as e:
        print(f"Error accessing camera: {e}")
        continue

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Reduce size for faster processing
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

            markAttendance(name)

    cv2.imshow('ESP32-CAM Face Recognition', img)
    key = cv2.waitKey(5)
    if key == ord('q'):
        break

cv2.destroyAllWindows()
