import os
import cv2
import numpy as np
from PIL import Image

# Inisialisasi recognizer wajah
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Lokasi folder dataset tempat gambar wajah disimpan
dataset_path = 'dataset'

# Pengecekan apakah folder dataset ada
if not os.path.exists(dataset_path):
    print(f"Error: Dataset folder '{dataset_path}' not found.")
    exit(0)

# Pengecekan apakah folder dataset tidak kosong
if len(os.listdir(dataset_path)) == 0:
    print(f"Error: No images found in the dataset folder '{dataset_path}'.")
    exit(0)

# Pengecekan apakah folder recognizer ada, jika tidak, buat folder tersebut
if not os.path.exists('recognizer'):
    os.makedirs('recognizer')

# Fungsi untuk mengambil gambar dan ID pengguna dari dataset
def getImagesWithID(path):
    # Ambil semua file gambar dari folder dataset
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.png')]
    
    faces = []
    IDs = []
    
    # Loop melalui semua gambar
    for imagePath in imagePaths:
        # Buka gambar dan ubah ke grayscale
        try:
            faceImg = Image.open(imagePath).convert('L')
            faceNp = np.array(faceImg, 'uint8')
        except Exception as e:
            print(f"Error loading image {imagePath}: {e}")
            continue
        
        # Ambil ID dari nama file (format: User.ID.SampleNum.jpg)
        try:
            ID = int(os.path.split(imagePath)[-1].split('.')[1])
        except IndexError:
            print(f"Error: Invalid file name format {imagePath}. Expected format: User.ID.SampleNum.jpg")
            continue
        
        # Tambahkan gambar wajah dan ID ke list
        faces.append(faceNp)
        IDs.append(ID)
        
        # Tampilkan gambar yang sedang diproses (opsional)
        cv2.imshow("Training", faceNp)
        cv2.waitKey(10)
    
    return np.array(IDs), faces

# Ambil ID dan gambar wajah dari dataset
Ids, faces = getImagesWithID(dataset_path)

# Cek apakah ada wajah yang ditemukan
if len(Ids) == 0 or len(faces) == 0:
    print("Error: No valid data found for training.")
    exit(0)

# Latih recognizer menggunakan gambar wajah dan ID
recognizer.train(faces, Ids)

# Simpan hasil training ke file yml
recognizer.save('recognizer/trainingData.yml')

# Tutup semua jendela tampilan
cv2.destroyAllWindows()
