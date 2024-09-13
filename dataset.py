import cv2
import os
import sqlite3

# Fungsi untuk membuat tabel People
def createTable():
    conn = sqlite3.connect("FaceBase.db")
    conn.execute('''CREATE TABLE IF NOT EXISTS People
           (ID INTEGER PRIMARY KEY NOT NULL,
           Name TEXT NOT NULL);''')
    conn.commit()
    conn.close()

# Fungsi untuk memasukkan data pengguna baru ke database
def insertOrUpdate(Id, Name):
    conn = sqlite3.connect("FaceBase.db")
    cmd = "SELECT * FROM People WHERE ID=?"
    cursor = conn.execute(cmd, (Id,))
    isRecordExist = 0
    for row in cursor:
        isRecordExist = 1
    if isRecordExist == 1:
        cmd = "UPDATE People SET Name=? WHERE ID=?"
        conn.execute(cmd, (Name, Id))
    else:
        cmd = "INSERT INTO People(ID, Name) VALUES(?, ?)"
        conn.execute(cmd, (Id, Name))
    conn.commit()
    conn.close()

# Panggil fungsi untuk membuat tabel
createTable()

# Pengecekan apakah file classifier tersedia
if not os.path.exists('Classifier/haarcascade_frontalface_default.xml'):
    print("Error: Classifier file not found.")
    exit(0)

# Inisialisasi pengenal wajah
faceDetect = cv2.CascadeClassifier('Classifier/haarcascade_frontalface_default.xml')

# Akses kamera
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Error: Could not open camera.")
    exit(0)

# Dapatkan ID dan Nama pengguna
Id = input('Masukkan ID pengguna: ')
Name = input('Masukkan Nama pengguna: ')

# Panggil fungsi untuk menyimpan atau memperbarui data pengguna di database
insertOrUpdate(Id, Name)

if not os.path.exists('dataset'):
    os.makedirs('dataset')

sampleNum = 0

while True:
    ret, img = cam.read()
    if not ret:
        print("Error: Failed to capture image.")
        break
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    
    for (x, y, w, h) in faces:
        sampleNum += 1
        cv2.imwrite(f"dataset/User.{Id}.{sampleNum}.jpg", gray[y:y+h, x:x+w])
        print(f"Captured image {sampleNum} for user {Name} with ID {Id}")
        
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow("Face", img)
    
    if sampleNum >= 20:
        break
    
    if cv2.waitKey(100) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()
