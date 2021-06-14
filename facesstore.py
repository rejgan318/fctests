"""

"""
import pathlib
import time
import enum
import json
import pickle

# class PhotoInfo:
#
#     def __init__(self, path: pathlib.Path):
#
#         # dump_file = path / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_PICKLE_SUFFIX)
#         # if dump_file.exists():
#         #     with open(dump_file, 'rb') as f:
#         #         self.__dict__.update(pickle.load(f).__dict__)
#         # else:
#         #     self.path_time = 0   # время последней модификации директории в секундах
#         #     self.num_photos = 0         # количество фото с найденны
#
#         self.path_time = 0   # время последней модификации директории в секундах
#         self.num_photos = 0         # количество фото с найденны
#
#         self.cwd = path.cwd()  # Текущая директория, из которой был запуск скагирования
#         self.path = path  # Параметр - директория сканирования относительно текущей
#         self.methods = SCAN_METHODS # возможные методы сканирования
#         self.name = SCAN_PHOTOS_NAME
#         self.version = SCAN_PHOTOS_VERSION  # Текущая версия
#         self.image_name = None
#         self.image = None
#         self.photos = {}
#
#     def save(self):
#         self.path_time = self.path.stat().st_mtime
#         # print(f'Время директории {str(self.path)} = {time.ctime(self.path_time)}.')
#
#         # class PathlibEncoder(json.JSONEncoder):
#         #     def default(self, obj):
#         #         if isinstance(obj, pathlib.WindowsPath):
#         #             return str(obj)
#         #         return json.JSONEncoder.default(self, obj)
#         #
#         # to_save = json.dumps(self.__dict__, indent=4, cls=PathlibEncoder)
#         # file2save = pathlib.Path(self.path) / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_JSON_SUFFIX)
#         # file2save.write_text(to_save)
#
#         # file2save = pathlib.Path(self.path) / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_PICKLE_SUFFIX)
#         # with open(file2save, "wb") as pickle_file:
#         with open(pathlib.Path(self.path) / (SCAN_PHOTOS_FILE_NAME + SCAN_PHOTOS_PICKLE_SUFFIX), "wb") as pickle_file:
#             pickle.dump(self, pickle_file)
#
#     def set_fr_boxes(self, boxes):
#         self.photos[self.image_name.name]['fr']['boxes'] = boxes
#         self.num_photos += len(boxes)
#         self.photos[self.image_name.name]['fr']['n'] = len(boxes)
#
#     def set_fr_enc(self, face_encodings):
#         self.photos[self.image_name.name]['fr']['enc'] = face_encodings
#
#     def set_image(self, image: pathlib.Path):
#         self.image_name = image
#         if not hasattr(self.photos, self.image_name.name):
#             self.photos[self.image_name.name] = {
#                 'dt': 0,
#                 'size': 0,
#                 'wh': [None, None],
#                 'fr': {
#                     'n': 0,
#                     'boxes': None,
#                     'enc': None,
#                 },
#                              }
#
#     def set_xmp(self, faces, wh):
#         self.photos[self.image_name.name]['wh'] = wh
#         self.photos[self.image_name.name]['faces'] = faces


class Method(enum.Flag):
    EXIF = enum.auto()
    FACE_RECOGNITION = enum.auto()
    CV2 = enum.auto()
    DLIB = enum.auto()
    MTCNN = enum.auto()


class FaceInfo:
    def __init__(self):
        self.name: str
        self.x1: int
        self.y1: int
        self.x2: int
        self.y3: int
        self.encode: dict = {}


class FacesStore:
    DEFAULT_NAME = 'photos'
    DEFAULT_EXT_PICLE = '.pickle'
    DEFAULT_EXT_JSON = '.json'
    JSON = 1
    PICKLE = 2

    PROGRAM = 'Face Store'
    VERSION = '0.2'

    def __init__(self, file_name: str = '', path: str = '.'):

        def _def_json_pickle_files():
            if self.file_name.lower().endswith(self.DEFAULT_EXT_JSON):
                self.store2pickle = False
                self.json_file = file_name
            elif self.file_name.lower().endswith(self.DEFAULT_EXT_PICLE):
                self.store2json = False
                self.pickle_file = file_name
            else:
                self.json_file = self.file_name + self.DEFAULT_EXT_JSON
                self.pickle_file = self.file_name + self.DEFAULT_EXT_PICLE
        self.program_name = self.PROGRAM
        self.version = self.VERSION      # Текущая версия
        self.time = time.time()
        self.file_name = file_name if file_name != '' else self.DEFAULT_NAME + self.DEFAULT_EXT_PICLE
        self.store2json = True
        self.store2pickle = True
        self.json_file = None
        self.pickle_file = None
        _def_json_pickle_files()
        self.path_name = path
        self.methods = None
        self.exif = None
        self.data = None        # данные для сохранения / считывания

    def is_exist(self, file_name: str = '', path: str = ''):
        """
        Проверка существования файлов json и pickle
        """
        file = self.file_name if file_name == '' else file_name
        if not file:
            return False
        path_name = self.path_name if path == '' else path
        return (pathlib.Path(path_name) / file).exists()


    def _parse_exif_in(self, data):
        return True

    def add_data(self, data, method: Method):
        if method == Method.EXIF:
            self.methods |= Method.EXIF
            self.exif = self._parse_exif_in(data)

    def save(self):
        pass

    def load(self):
        pass

if __name__ == '__main__':
    # print('Тест на первоначальную инициализацию')
    # for param in [('',), ('mystore',), ('mystore.JSON', '../source'), ('mystore.pickle', 'mydir')]:
    #     print(param, "\n\t\t", FacesStore(*param).__dict__)

    # print('Тест на is_exis')
    # t = FacesStore()
    # for test in [('', ''), ('photos.pickle', 'testpict'), ('photos.json', 'testpict'), ('photos.', 'testpict/anna'), ]:
    #     if t.is_exist(test[0], test[1]):
    #         print('Есть файл хранилища лиц', test[0], 'в директории', test[1])
    #     else:
    #         print('Отсутствует файл ', test[0], 'в директории', test[1])

    # print('Тест на флаги методов enum.Flag')
    # flag = Method.EXIF | Method.CV2 | Method.FACE_RECOGNITION
    # print(bool(flag & Method.DLIB))
    # print(bool(flag & Method.CV2))

    print('Done')
