import os
from pathlib import Path
from PIL import Image
import imagehash
import sqlite3

filePath = Path(input("Drag and drop the file here and press Enter:").strip("'"))

conn = sqlite3.connect(str(filePath / 'data.db'))

cursor = conn.cursor()

cursor.execute('''
                CREATE TABLE IF NOT EXISTS files (
                    name TEXT PRIMARY KEY,
                    hash TEXT NOT NULL
               )
               ''')

conn.commit()

def isImg(imgPath):
    fileExtension = imgPath.suffix
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.ico', '.webp'}
    return fileExtension in image_extensions

def addToDB(name, hash):
    cursor.execute('''
        INSERT INTO files (name, hash)
        VALUES (?, ?)
        ''', (name, hash))
    conn.commit()

for file in filePath.iterdir():
    if isImg(file):
        imgFile = Image.open(file)
        imgHash = str(imagehash.average_hash(imgFile))
        cursor.execute('SELECT name, hash FROM files WHERE hash = ?', (imgHash,))
        result = cursor.fetchone()

        if result is None:
            addToDB(file.name, imgHash)
        else: 
            if len(result[0]) > len(file.name):
                cursor.execute('UPDATE files SET name = ? WHERE hash = ?', (file.name, imgHash))
                os.remove(str(filePath / result[0]))
            else: 
                os.remove(str(filePath / file.name))

conn.close()

os.remove(str(filePath / 'data.db'))