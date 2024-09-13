import cv2  # Library untuk mengolah gambar (Face Recognition)
import numpy as np  # Library untuk mengolah data matrix dalam gambar/video
from PIL import Image  # Library untuk mengolah gambar
import pickle  # Library untuk mengolah data
import sqlite3  # Library untuk mengolah database
import time  # Library untuk delay
import RPi.GPIO as GPIO  # GPIO
import board
import digitalio
from adafruit_character_lcd.character_lcd_rgb_i2c import Character_LCD_RGB_I2C

# Inisialisasi pin servo
servoPin = 17  
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPin, GPIO.OUT)
GPIO.setwarnings(False)
p = GPIO.PWM(servoPin, 50)  # GPIO17 for PWM with 50Hz
p.start(2.)  # Initialization
p.ChangeDutyCycle(5)

# Init push button
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Setup untuk LCD I2C
lcd_i2c = Character_LCD_RGB_I2C(board.I2C(), 16, 2)  # 16x2 LCD
lcd_i2c.color = [100, 0, 0]  # Set warna LCD RGB
lcd_i2c.message = "LOCKED"

# Inisialisasi face recognizer
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("recognizer/trainingData.yml")
faceDetect = cv2.CascadeClassifier('Classifier/haarcascade_frontalface_default.xml')
path = 'dataSet'

# Fungsi untuk mendapatkan profile dari database
def getProfile(id):
    conn = sqlite3.connect("FaceBase.db")
    cmd = "SELECT * FROM People WHERE ID=" + str(id)
    cursor = conn.execute(cmd)
    profile = None
    for row in cursor:
        profile = row
    conn.close()
    return profile

# Pengaturan FPS
cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(3, 480)  # Setting Panjang Layar Kamera
cam.set(4, 360)  # Setting Lebar layar kamera

# Init font
font = cv2.FONT_HERSHEY_COMPLEX_SMALL
lock = 1  # init lock

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)  # Deteksi wajah
    
    button = GPIO.input(18)

    # Kondisi tombol
    if button == GPIO.HIGH:
        lock = 1

    # Kondisi kunci
    if lock == 1:
        lcd_i2c.clear()
        lcd_i2c.message = "LOCKED"
        p.ChangeDutyCycle(5)  # Locked position
    else:
        p.ChangeDutyCycle(15)  # Unlocked position

    for (x, y, w, h) in faces:
        id, conf = rec.predict(gray[y:y+h, x:x+w])
        print(conf)
        
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        profile = getProfile(id)

        if conf < 60:
            if profile is not None:
                lock = 0
                lcd_i2c.message = "UNLOCKED\nHello " + str(profile[1])
                cv2.putText(img, str(profile[1]), (x, y+h+30), font, 0.55, (0, 255, 0), 1)
                cv2.putText(img, str(profile[2]), (x, y+h+60), font, 0.55, (0, 255, 0), 1)
                cv2.putText(img, str(conf), (x, y+h+120), font, 0.55, (0, 255, 0), 1)
        else:
            cv2.putText(img, "Unknown", (x, y+h+30), font, 0.55, (0, 255, 0), 1)
            cv2.putText(img, str(conf), (x, y+h+60), font, 0.55, (0, 255, 0), 1)

    cv2.imshow("Face", img)

    if cv2.waitKey(1) == ord('q'):
        break

# Cleanup GPIO saat keluar dari loop
cam.release()
cv2.destroyAllWindows()
GPIO.cleanup()
