import face_recognition
import cv2
import numpy as np
from datetime import datetime
import pyodbc

# Connect to SQL Server
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=YOURS\HELLOSQL;DATABASE=SDdatabase;UID=sa;PWD=hello@123')
cursor = conn.cursor()

# Load the known student faces and names from the database
known_face_encodings = []
known_face_names = []

# Assuming you have a table named 'sinh_vien_info' with columns 'student_id', 'first_name', and 'last_name'
cursor.execute("SELECT student_id, first_name, last_name FROM sinh_vien_info")
for row in cursor.fetchall():
    student_id, first_name, last_name = row
    image = face_recognition.load_image_file(f"student_images/{student_id}.jpg")
    face_encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(face_encoding)
    known_face_names.append(f"{first_name} {last_name}")

# Start the webcam
video_capture = cv2.VideoCapture(0)

while True:
    # Capture a frame from the webcam
    ret, frame = video_capture.read()

    # Resize the frame to improve performance
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Loop through each face in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Scale the bounding box coordinates back up to the original image size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # See if the face is a match for the known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # If a match was found, use the name
        if True in matches:
            first_name, last_name = known_face_names[matches.index(True)].split()
            name = f"{first_name} {last_name}"

            # Update the attendance in your database
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO attendance (student_id, first_name, last_name, date, time) VALUES (?, ?, ?, ?, ?)",
                          (cursor.lastrowid, first_name, last_name, current_time.split()[0], current_time.split()[1]))
            conn.commit()

        # Draw a rectangle around the face and the name
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Facial Recognition and Attendance', frame)

    # Press 'q' to quit the application
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the database connection
video_capture.release()
conn.close()
cv2.destroyAllWindows()