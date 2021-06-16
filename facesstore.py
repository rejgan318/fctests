"""

"""
import enum
import json
import pathlib
import pickle
import time
import colorama
from pydantic import BaseModel

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
    """ Флаги методов распознования """
    EXIF = enum.auto()
    FACE_RECOGNITION = enum.auto()
    CV2 = enum.auto()
    DLIB = enum.auto()
    MTCNN = enum.auto()


class FaceInfo:
    def __init__(self, Name: str = None, Type: str = None, Rotation: float = None, h: float = None, w: float = None,
                 x: float = None, y: float = None, x1: int = None, y1: int = None, x2: int = None, y2: int = None, ):
        self.Name: str = Name
        self.Type: str = Type
        self.Rotation: float = Rotation
        self.h: float = h
        self.w: float = w
        self.x: float = x
        self.y: float = y
        self.x1: int = x1
        self.y1: int = y1
        self.x2: int = x2
        self.y2: int = y2
        # self.encode: dict = {}


class ForSave:
    def __init__(self):
        self.exif: list


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
        self.version = self.VERSION  # Текущая версия
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
        self.data = {}  # данные для сохранения / считывания

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
        for file_name, exif_faces in data.items():
            if not self.data.get(file_name, False):
                self.data[file_name] = ForSave()
            self.data[file_name].exif = []
            for one_face in exif_faces:
                self.data[file_name].exif.append(FaceInfo(**one_face))
        return True

    def add_data(self, data, method: Method):
        if method == Method.EXIF:
            self.methods = (self.methods | Method.EXIF) if self.methods else Method.EXIF
            self.exif = self._parse_exif_in(data)

    def save(self):
        if self.pickle_file:
            with open(self.pickle_file, 'wb') as f:
                pickle.dump(self.data, f)
        print('Записано ПИкле')
        # if self.json_file:
        #     with open(self.json_file, 'w', encoding='utf-8') as f:
        #         json.dump(self.data, f, indent=4, ensure_ascii=False)
        # print('Записано Джсон')

    def load(self):
        pass


def get_files_by_mask(files: list[str], mask: str = "*.jpg", local: bool = False) -> list:
    """
    по списку директорий сформировать список файлов с заданным расширением, входящих в поддиректории тоже
    Используется: pathlib
    Ограничение: имена директории и поддиректории не должны заканчиваться на маску расширения, иначе они попадут в
        формируемый список файлов
    :param files: список имен директорий, файлов
    :param mask: маска расширения файла
    :param local: если True, то поиск без поддиректорий
    :return: список найденных файлов
    """
    files_by_mask = []
    for cur_dir in files:
        if pathlib.Path(cur_dir).is_dir():
            cur_files = pathlib.Path(cur_dir).glob(("**/" if not local else "") + mask)
        else:  # Файл в параметрах
            cur_files = [pathlib.Path(cur_dir)]
        files_by_mask += cur_files
    return files_by_mask


def get_dirs(photos: list) -> dict:
    """
    Из полного списка файлов вернуть словарь
        ключ - имя директории
        значение - список файлов в этой директории
    """
    dirs_photos = {}  # рабочий словарь с ключом имя-директории и данными для сохранения
    for i in range(len(photos)):
        photo = str(photos[i])
        d_photo = str(pathlib.Path(photo).parent.resolve())
        if dirs_photos.get(d_photo, False):
            dirs_photos[d_photo].append(pathlib.Path(photo).name)
        else:
            dirs_photos[d_photo] = [pathlib.Path(photo).name]  # новая директория, начинаем список с текущего файла
    return dirs_photos

cm: str = lambda s: colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Fore.RESET
cg: str = lambda s: colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Fore.RESET


def short_list(long_list: list, max_len: int = 5, separator: str = ', ', hidden_num: bool = True) -> str:
    """
    Сокращенный вид списка для печати
    :param long_list: Исходный список большой длины, который не удобно выводить на печать
    Ограничение: элементы списка должны без ошибок преобразовываться к str
    :param max_len: количество элементом списка, которые будут выводиться без сокращения
    :param separator: разделитель для join
    :param hidden_num: печать количество пропущенных элементов
    :return: строка из первых max_len-1 элементов, ' ... ' и последний элемент
    """
    if len(long_list) > max_len:
        return separator.join(map(str, long_list[:max_len - 1])) + f'{separator}...' + \
               (f'({len(long_list) - max_len})...' if hidden_num else '') + ' ' + str(long_list[-1])
    else:
        return separator.join(map(str, long_list[:max_len]))

if __name__ == '__main__':

    print('Тест на первоначальную инициализацию')
    # for param in [('',), ('mystore',), ('mystore.JSON', '../source'), ('mystore.pickle', 'mydir')]:
    #     print(param, "\n\t\t", FacesStore(*param).__dict__)

    print('Тест на is_exis')
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

    print('Тест на short_list')
    # for test_list in [
    #     {'long_list': ['1', 2, '3', '4', '5', 6, ], 'max_len':5, 'separator': ' '},
    #     {'long_list': ['-----1-----', '-2-']*10, 'max_len':15, },
    #     {'long_list': ['1']*100, 'max_len':10, },
    #     {'long_list': ['1']*100, },
    #     {'long_list': [1.]*100, },
    #     {'long_list': ['1']*100, 'hidden_num': False},
    #     {'long_list': range(1000, 500, -10), 'max_len': 20, },
    #     {'long_list': range(1000, 500, -10), 'max_len': 45, },
    # ]:
    #     print(f'{short_list(**test_list)}')

    print('Тест на get_files_by_mask и get_dirs')
    # for test in [('testpict testpict/anna', True), ('testpict', False), ('../scrapered_pictures', False), ]:
    #     files = test[0].split()
    #     local = test[1]
    #     photo_files = get_files_by_mask(files=files, local=local)
    #     print(f'Всего {cm(len(photo_files))} в {cm(test[0])} {"с поддиректориями" if not local else ""} ')
    #     for cur_dir, files_in_dir in get_dirs(photo_files).items():
    #         print(f'{cm(len(files_in_dir))} файлов в {cur_dir}: {short_list(files_in_dir, )}')


    print(cg('Done'))
