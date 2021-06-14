"""
Тестирование, cv2 face detection в многопоточном режиме
"""
import pathlib
import argparse
import csv
import colorama
import cv2

CSV_FILE = 'faces.csv'

ap = argparse.ArgumentParser(description='Список всех jpg в файл')
ap.add_argument('directory', type=str, nargs='*', default='.', help='Спикок директорий с jpg. По умолчанию текущая', )
ap.add_argument('--local', '-l', default=False, action='store_true',
                help='Без вложенных директорий. По умолчанию с поддиректориями', )
pars = ap.parse_args('testpict'.split())
# pars = ap.parse_args('testpict ../scrapered_pictures/done1'.split())

print('Считаем из файла ранее созраненное из ' + CSV_FILE)
photos_expected = {}
with open(CSV_FILE, 'r', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ')
    for row in spamreader:
        photos_expected[row[1]] = int(row[0])
print('Прописано количество лиц для ', len(photos_expected), ' файлов')
# Считали прописанные вручную количества лиц для каждого файла

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
i = 1
total_face_true, total_face_cv2 = 0, 0
for photo, faces_expected in photos_expected.items():
    imgcv = cv2.imread(photo)
    gray = cv2.cvtColor(imgcv, cv2.COLOR_BGR2GRAY)
    # faces = face_cascade.detectMultiScale(gray)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=8)
    print(f'{colorama.Fore.LIGHTCYAN_EX}{i:3}{colorama.Fore.RESET} {photo:30} '
          f'{colorama.Fore.LIGHTGREEN_EX}{faces_expected}{colorama.Fore.RESET}/'
          f'{colorama.Fore.LIGHTCYAN_EX}{len(faces)}{colorama.Fore.RESET}')
    save_photo(photo, imgcv, faces)
    i += 1
    total_face_true += faces_expected
    total_face_cv2 += len(faces)

print("Ожидается всего", total_face_true, "найдено всего", total_face_cv2)