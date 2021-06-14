"""
Директорию с поддиректориями
выбрать все *.jpg
проверить нгаличие служебного файла SCAN_PHOTOS_FILE_NAME
если его нет - сгенерировать
"""

import argparse
import pathlib
# import time
import colorama
import face_recognition
# import json
import pickle
import xmpfaces
import PIL
import cv2

SCAN_PHOTOS_FILE_NAME = "scanphotos"
SCAN_PHOTOS_JSON_SUFFIX = ".json"
SCAN_PHOTOS_PICKLE_SUFFIX = ".dump"

SCAN_PHOTOS_NAME = "Scan Photos"    # имя программы
SCAN_PHOTOS_VERSION = "0.2"  # Текущая версия
SCAN_METHODS = {'fr': 'face_recognition', 'exif': 'exif'}

colorama.init(autoreset=True)


def get_params():
    """
    Обработка параметров одной из стандартных библиотек
    :return: параметры командной строки, объект
    """
    parcer = argparse.ArgumentParser(description='Просмотр фотографий или изображений')
    parcer.add_argument('dirs', type=str, help='Директория с фотографиями')
    return parcer.parse_args()


class PhotoInfo:

    def __init__(self, path: pathlib.Path):

        # dump_file = path / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_PICKLE_SUFFIX)
        # if dump_file.exists():
        #     with open(dump_file, 'rb') as f:
        #         self.__dict__.update(pickle.load(f).__dict__)
        # else:
        #     self.path_time = 0   # время последней модификации директории в секундах
        #     self.num_photos = 0         # количество фото с найденны

        self.path_time = 0   # время последней модификации директории в секундах
        self.num_photos = 0         # количество фото с найденны

        self.cwd = path.cwd()  # Текущая директория, из которой был запуск скагирования
        self.path = path  # Параметр - директория сканирования относительно текущей
        self.methods = SCAN_METHODS # возможные методы сканирования
        self.name = SCAN_PHOTOS_NAME
        self.version = SCAN_PHOTOS_VERSION  # Текущая версия
        self.image_name = None
        self.image = None
        self.photos = {}

    def save(self):
        self.path_time = self.path.stat().st_mtime
        # print(f'Время директории {str(self.path)} = {time.ctime(self.path_time)}.')

        # class PathlibEncoder(json.JSONEncoder):
        #     def default(self, obj):
        #         if isinstance(obj, pathlib.WindowsPath):
        #             return str(obj)
        #         return json.JSONEncoder.default(self, obj)
        #
        # to_save = json.dumps(self.__dict__, indent=4, cls=PathlibEncoder)
        # file2save = pathlib.Path(self.path) / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_JSON_SUFFIX)
        # file2save.write_text(to_save)

        # file2save = pathlib.Path(self.path) / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_PICKLE_SUFFIX)
        # with open(file2save, "wb") as pickle_file:
        with open(pathlib.Path(self.path) / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_PICKLE_SUFFIX), "wb") as pickle_file:
            pickle.dump(self, pickle_file)

    def set_fr_boxes(self, boxes):
        self.photos[self.image_name.name]['fr']['boxes'] = boxes
        self.num_photos += len(boxes)
        self.photos[self.image_name.name]['fr']['n'] = len(boxes)

    def set_fr_enc(self, face_encodings):
        self.photos[self.image_name.name]['fr']['enc'] = face_encodings

    def set_image(self, image: pathlib.Path):
        self.image_name = image
        if not hasattr(self.photos, self.image_name.name):
            self.photos[self.image_name.name] = {
                'dt': 0,
                'size': 0,
                'wh': [None, None],
                'fr': {
                    'n': 0,
                    'boxes': None,
                    'enc': None,
                },
                             }

    def set_xmp(self, faces, wh):
        self.photos[self.image_name.name]['wh'] = wh
        self.photos[self.image_name.name]['faces'] = faces


# '🤖🤡'
photos_path = pathlib.Path("testpict")
# photos_path = pathlib.Path(r"..\scrapered_pictures\done1")
# photos_path = pathlib.Path(r"..\scrapered_pictures\gone1")
scan_photos = [x for x in photos_path.rglob('*.jpg') if x.is_file()]

print(f"\n           === {colorama.Fore.GREEN}Обработка фотографий, распознование лиц{colorama.Fore.RESET} ===\n")
print(f'{colorama.Fore.LIGHTMAGENTA_EX}5{colorama.Fore.RESET} - 5 лиц счиано из EXIF; '
      f'{colorama.Fore.LIGHTRED_EX}4{colorama.Fore.RESET} - 4 найдено с помощью face_recognition; '
      f'{colorama.Fore.LIGHTCYAN_EX}🤖{colorama.Fore.RESET} - лица декодированы face_encodings.\n')
print(f"Директория {colorama.Fore.LIGHTGREEN_EX}{photos_path}{colorama.Fore.RESET} с поддиректоориями содержит "
      f"{colorama.Fore.LIGHTGREEN_EX}{len(scan_photos)}{colorama.Fore.RESET} фотографмй для обработки")
curdir = ""
file_index = 0
files_in_row = 0
for photo in scan_photos:
    file_index += 1
    files_in_row += 1
    if files_in_row == 10:
        print(f'  {colorama.Fore.LIGHTGREEN_EX}{int((file_index - 1) / len(scan_photos) * 100)}%{colorama.Fore.RESET}')
        files_in_row = 0
    if photo.parent != curdir:
        files_in_row = 0
        curdir = photo.parent
        curdir_photos = [p for p in scan_photos if p.parent == curdir]
        print(f'\n{colorama.Style.BRIGHT}{curdir}{colorama.Style.NORMAL} содержит '
              f'{colorama.Fore.LIGHTGREEN_EX}{len(curdir_photos)}{colorama.Fore.RESET} фото, '
              f' прогресс {colorama.Fore.LIGHTGREEN_EX}{int((file_index - 1)/ len(scan_photos) * 100)}%{colorama.Fore.RESET}')
        sf = PhotoInfo(curdir)

    sf.set_image(photo)
    print(f'{photo.name} ', end='')

    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    # Read the input image
    imgcv = cv2.imread(str(photo))
    # Convert into grayscale
    gray = cv2.cvtColor(imgcv, cv2.COLOR_BGR2GRAY)
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    # Draw rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(imgcv, (x, y), (x + w, y + h), (255, 0, 0), 2)
    # Display the output
    if len(faces):
        cv2.imshow('img', imgcv)
        cv2.waitKey()
    # print("cv2")

    pil_photo = PIL.Image.open(str(photo))
    faces, wh = xmpfaces.xmpfaces(pil_photo)
    sf.set_xmp(faces, wh)
    print(f'{colorama.Fore.LIGHTMAGENTA_EX}{len(faces)}{colorama.Fore.RESET}/', end='')

    im_photo = face_recognition.load_image_file(photo)
    # faces_boxes = sf.get_state("fr", "boxes")
    # if not faces_boxes:
    faces_boxes = face_recognition.face_locations(im_photo)
    # print(f' {colorama.Fore.LIGHTGREEN_EX}🤡{colorama.Fore.RESET}', end='')
    sf.set_fr_boxes(faces_boxes)
    print(f'{colorama.Fore.LIGHTRED_EX}{len(faces_boxes)}{colorama.Fore.RESET} ', end='')
    if len(faces_boxes):
        faces_recogn = face_recognition.face_encodings(im_photo)
        sf.set_fr_enc(faces_recogn)
        print(f' {colorama.Fore.LIGHTCYAN_EX}🤖{colorama.Fore.RESET}  ', end='')

    sf.save()

print('Done')
