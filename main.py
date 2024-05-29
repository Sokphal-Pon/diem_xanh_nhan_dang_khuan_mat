import cv2
import face_recognition
import os
import pickle
import numpy as np
import cvzone
from datetime import datetime 
import pyodbc

# Connect to SQL Server
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=YOURS\HELLOSQL;DATABASE=SDdatabase;UID=sa;PWD=hello@123')
cursor = conn.cursor()

# Open Camera
cap = cv2.VideoCapture(0)
storage = cv2.imread("images")
# location main folder form
imgBackground = cv2.imread("form/imgBackground.png")
# 2nd location folder form
folderModePath = 'form/form2'
modePathList = os.listdir(folderModePath)
imgInForm2 = []
for path in modePathList:
    imgInForm2.append(cv2.imread(os.path.join(folderModePath, path)))

# Load trainning facail saved
file = open('trainFiles.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentID = encodeListKnownWithIds
#print(studentID)
print("Model is Loading...")

# Action mode of the form
form2 = 0
counter = 0
id = -1
imgStudents = []

while True:
    video, img = cap.read()

    # Resize image from database
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    # Detecting the face in the image
    faceCurFrame = face_recognition.face_locations(imgS)
    CurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    # Resize Video fram and display form
    img = cv2.resize(img, (720,480))
    imgBackground[91:91 + 480, 54:54 + 720] = img
    imgBackground[28:28 + 663, 822:822 + 436] = imgInForm2[form2]

    # find and match the face in the image for the saved face trainFiles.Zip
    for saveFace, faceLoc in zip(CurFrame, faceCurFrame):
        match = face_recognition.compare_faces(encodeListKnown, saveFace)
        faceDis = face_recognition.face_distance(encodeListKnown, saveFace)
        #print(match)
        #print(faceDis)

        # print matching face to display the name of the person
        matchIndex = np.argmin(faceDis)
        #print("Match Index", matchIndex)
        if match[matchIndex]:
            #print("Your Face Detected")
            #print(studentID[matchIndex])

            # Drawing rectangle and bounding-box around the face
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 3 , x2 * 3, y2 * 3, x1 * 3
            boundingBox = 54 + x1, 70 + y1, x2-x1, y2-y1
            imgBackground = cvzone.cornerRect(imgBackground, boundingBox, rt=0)
            id = studentID[matchIndex]
            #print(id)
            if counter == 0:
                counter = 1
                form2 = 1
    cv2.putText(imgBackground, "Scanning...", (349, 637),
                    cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)
        

    if counter != 0:
    # get data from database
        if counter == 1:
            cursor.execute("SELECT * FROM sinh_vien_info")
            studentInfo = cursor.fetchone(f'sinh_vien_info/{id}').get()
            #print(studentInfo)

            # get image from storage firebase
            stor = storage.bucket().blob(f'images/{id}.png')
            array = np.frombuffer(stor.download_as_string(), np.uint8)  
            imgStudents = cv2.imdecode(array, cv2.COLOR_BGRA2BGR) 

            # Insert date & time to database
            datetimeObject = datetime.strptime(studentInfo['last_time_scan'],
                                                   "%Y-%m-%d %H:%M:%S")
            secondsElapsed = (datetime.now() - datetimeObject).total_seconds()
            #print(secondsElapsed)

            # Wait for time delay 60 seconds
            if secondsElapsed > 30:
                ref = cursor.fetchone(f'sinh_vien_info/{id}')
                # Update data to database
                studentInfo['totalScan'] = str(int(studentInfo['totalScan']) + 1)
                ref.child('totalScan').set(studentInfo['totalScan'])
                ref.child('last_time_scan').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            else:
                form2 = 4
                counter = 0
                imgBackground[28:28 + 663, 822:822 + 436] = imgInForm2[form2]

        # between 70->90 seconds show form 3
        if 70 <counter< 90:
            form2 = 3

        # show form 4
        if form2 != 4:
            if counter <=70:    
                # Display data from database
                cv2.putText(imgBackground, str(id), (1015, 246), 
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)
                
                cv2.putText(imgBackground, str(studentInfo['name']), (985, 311), 
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)
                
                cv2.putText(imgBackground, str(studentInfo['birthday']), (985, 350), 
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 1)
                
                cv2.putText(imgBackground, str(studentInfo['email']), (985, 388), 
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 0), 1)
                
                cv2.putText(imgBackground, str(studentInfo['major']), (985, 426),                    
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 1)
                
                cv2.putText(imgBackground, str(studentInfo['year_finish']), (985, 464),                   
                            cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 0, 0), 1)
                
                cv2.putText(imgBackground, str(studentInfo['totalScan']), (985, 502),                 
                            cv2.FONT_HERSHEY_COMPLEX, 0.7, (0, 0, 0), 1)
            
                #imgResize = cv2.resize(imgStudents, (200, 200))
                imgBackground[60:60 + 154, 956:956 + 168] = imgStudents

            # between 90->120 seconds show form 2
            if 90 <counter< 120:
                form2 = 2
                imgBackground[60:60 + 154, 956:956 + 168] = imgStudents

            # Keep it running
            counter+=1

            if counter >= 120:
                counter = 0
                form2 = 0
                studentInfo = []
                imgStudents = []
                imgBackground[28:28 + 663, 822:822 + 436] = imgInForm2[form2]
        else:
            imgBackground[60:60 + 154, 956:956 + 168] = imgStudents

    # back to oreginal form
    else:
        form2 = 0
        counter = 0

    #cv2.imshow ("video Cupture", img)
    cv2.imshow ("STUDENT ATTENDEANCE SYSTEM", imgBackground)

    # Close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
    

