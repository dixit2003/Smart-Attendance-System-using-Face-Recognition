import os
import pickle
from datetime import datetime

import cv2
import cvzone
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db

cred = credentials.Certificate("C:\\Users\\Sai Dixit\\PycharmProjects\\FacialAttendanceSystem\\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendancesystem-a2c47-default-rtdb.firebaseio.com/",
    'storageBucket': 'faceattendancesystem-a2c47.appspot.com'
})
bucket = storage.bucket()

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# Importing the mode images into a list
imgBackground = cv2.imread('C:\\Users\\Sai Dixit\\PycharmProjects\\FacialAttendanceSystem\\Resources\\background.jpg')
folderModePath = 'C:\\Users\\Sai Dixit\\PycharmProjects\\FacialAttendanceSystem\\Resources\Modes'
folderPath = 'C:\\Users\\Sai Dixit\\PycharmProjects\\FacialAttendanceSystem\\Images'
modePathList = os.listdir(folderModePath)  # Gives the list of png files in Modes
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
# print(len(imgModeList))

# Creating a dictionary of names with their corresponding ids
imgPath = 'C:\\Users\\Sai Dixit\\PycharmProjects\\FacialAttendanceSystem\Images'
images = []
ids = []
names = ['Sai Dixit Vila', 'Shashwat', 'Jennifer', 'Jefferson', 'Elon Musk']
classNames = {}

imgPathList = os.listdir(imgPath)
print(imgPathList)
for img in imgPathList:
    curImg = cv2.imread(f'{imgPath}/{img}')
    images.append(curImg)
    ids.append(os.path.splitext(img)[0])

# print(ids)

classNames = {k: v for k, v in zip(ids, names)}
print(classNames)

# Load the encoding file
print("Loading Encode File...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print(studentIds)
print("Encode File Loaded...")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)  # Scaling down the image to 1/4th as it takes a lot of computation power
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrFrame = face_recognition.face_locations(imgS)  # Detects the current face frame
    encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)  # Finds the encodings of the current detected face

    imgBackground[162:162 + 480, 55:55 + 640] = img  # Overlaying the image upon the background template
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    if faceCurrFrame:

        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            print("Matches:", matches)
            print("Face Distance:", faceDis)

            matchIndex = np.argmin(faceDis)  # Returns the index with the min face distance as that will be the match
            # print("Match Index",matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected!")
                id = studentIds[matchIndex]  # Retrieving ID of student whose face is detected

                name = classNames[id].upper()

                y1, x2, y2, x1 = faceLoc  # Mapping the face locations
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scaling up 4 times coz it was scaled down previously
                bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1  # Creating the bounding box (x,y,w,h)
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)  # Rectangle thickness (rt)

                # cv2.rectangle(imgBackground, bbox, (0, 255, 0), 2)
                # cv2.rectangle(imgBackground, (x1, y2 - 35), (x2, y2), (0, 250, 0), cv2.FILLED)
                cv2.putText(imgBackground, name, (x1, y2 + 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

                if counter == 0:
                    # cvzone.putTextRect(imgBackground, "Loading", (275, 400))
                    cv2.imshow("Smart Attendance System", imgBackground)
                    counter = 1
                    modeType = 1
                    cv2.waitKey(1)

        if counter != 0:

            # Only in the first frame the download of student data happens
            if counter == 1:
                # Get the data
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                # Get image from storage bucket
                blob = bucket.get_blob(f'{folderPath}/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                imgStudent = cv2.resize(imgStudent, (216, 216))

                # Updating the data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'], '%Y-%m-%d %H:%M:%S')
                secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:

                if 10 < counter < 20:
                    modeType = 2

                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:
                    cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(id), (1006, 493), cv2.FONT_HERSHEY_COMPLEX, 0.5,
                                (255, 255, 255), 1)
                    cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625), cv2.FONT_HERSHEY_COMPLEX,
                                0.6,
                                (100, 100, 100), 1)
                    cv2.putText(imgBackground, str(studentInfo['progress']), (910, 625), cv2.FONT_HERSHEY_COMPLEX, 0.6,
                                (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2
                    cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445), cv2.FONT_HERSHEY_COMPLEX, 1,
                                (50, 50, 50), 1)

                    # Assign the resized imgStudent to the specified region in imgBackground
                    imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

                counter += 1

                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    else:
        modeType = 0
        counter = 0

    # cv2.imshow("Webcam",img)
    cv2.imshow("Smart Attendance System", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
