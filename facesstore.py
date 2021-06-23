"""
Интерфайс между модулями распознования лиц и json-файлом хоанения результатов
"""
from enum import IntFlag
from pathlib import Path
import time
from pydantic import BaseModel


class Method(IntFlag):
    """ Флаги методов распознования """
    EXIF = 1
    FACE_RECOGNITION = 2
    CV2 = 4
    DLIB = 8
    MTCNN = 16


class FaceInfo(BaseModel):
    name: str = None
    type_region: str = None
    rotation: float = None
    h: float = None
    w: float = None
    x: float = None
    y: float = None
    x1: int
    y1: int
    x2: int
    y2: int


class PhotoFile(BaseModel):
    name: str
    width: int = None
    height: int = None
    faces_exif: list[FaceInfo] = []
    faces_cv2: list[FaceInfo] = []


class Photos(BaseModel):
    program_name: str = 'Face Store'
    version: str = '0.4'  # Текущая версия
    descriptions: str = ''
    methods: Method
    time: str = time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime())
    photos: dict[str, dict[str, PhotoFile]] = {}

    def get_photo(self, dir_name: str, file_name: str) -> PhotoFile:
        if self.photos.get(dir_name, None):
            return self.photos[dir_name].get(file_name, None)


class FacesStore:
    DEFAULT_EXT: str = '.json'
    DEFAULT_NAME: str = 'fs'
    DEFAULT_MASK = ['jpg']

    def __init__(self, dirs: list[Path] = None,
                 local: bool = False,
                 mask: list[str] = None,
                 json_file: str = None,
                 description: str = None):

        self.dirs_names: list[Path] = dirs  # список имен директорий, файлов
        self.local: bool = local  # если True, то поиск без поддиректорий
        self.mask: list[str] = mask or self.DEFAULT_MASK  # список расширений обрабатываемых файлов
        self.json_file: Path = None
        if not json_file or json_file == '':
            self.json_file = Path(self.DEFAULT_NAME + self.DEFAULT_EXT)
        elif not Path(json_file).suffix:
            self.json_file = Path(json_file + self.DEFAULT_EXT)
        else:
            self.json_file = Path(json_file)
        self.description: str = description

        self.time = time.time()
        self.methods = None
        self.exif = None
        self.dirs: dict = {}
        self.files: list[Path] = []
        if self.dirs_names:
            self.get_files()
            self.get_dirs()
        self.photos: dict = {}  # данные для сохранения / считывания

    def get_files(self):
        """
        по списку директорий сформировать список файлов с заданным расширением, входящих в поддиректории тоже
        Ограничение: имена директории и поддиректории не должны заканчиваться на маску расширения, иначе они попадут в
            формируемый список файлов
        """
        for cur_dir in self.dirs_names:
            if cur_dir.is_dir():
                cur_files = []
                for m in self.mask:
                    cur_files += cur_dir.glob(("**/" if not self.local else "") + '*.' + m)
            else:  # Файл в параметрах, не опрабатываем
                cur_files = [cur_dir]
            self.files += cur_files
        # self.files.sort()

    def get_dirs(self, dirs: list[Path] = None, local: bool = None):
        """
        Из полного списка файлов вернуть словарь
            ключ - имя директории
            значение - список файлов в этой директории
        Вызывается из __init__ если указано dirs или позже с указанием dirs и возможно нового значения local
        """
        if dirs:
            self.dirs_names = dirs
            self.local = self.local if local is None else local  # новое значение, если указано
            self.get_files()
        # рабочий словарь с ключом имя-директории и данными для сохранения
        for photo in self.files:
            d_photo = str(photo.parent.resolve())
            if self.dirs.get(d_photo, False):
                self.dirs[d_photo].append(photo.name)
            else:
                self.dirs[d_photo] = [photo.name]  # новая директория, начинаем список с текущего файла
        # return dirs_photos

    def _parse_exif(self, dir: str, file: str, data: dict, faces: list[dict]):
        data_faces = [FaceInfo(**p) for p in faces]
        if not self.photos.get(dir, None):
            self.photos[dir] = {}
        if not self.photos[dir].get(file, None):
            self.photos[dir][file] = PhotoFile(name=file, width=data['width'], height=data['height'],
                                               faces_exif=data_faces)
        else:
            self.photos[dir][file].faces_exif = data_faces

    def add_data(self, method: Method, dir: str, file: str, data: dict, faces: list[dict]):
        if method == Method.EXIF:
            self.methods = (self.methods | Method.EXIF) if self.methods else Method.EXIF
            self._parse_exif(dir=dir, file=file, data=data, faces=faces)

    def save(self, json_file: str = None, description: str = ''):
        photos = Photos(descriptions=description, methods=self.methods, photos=self.photos)
        json_file = Path(json_file) if json_file else self.json_file
        json_file.write_text(photos.json(indent=2, ensure_ascii=False), encoding='utf-8')

    @classmethod
    def load(cls, json_file: str) -> Photos:
        return Photos.parse_file(json_file)


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
    import colorama
    from PIL import Image
    from xmpfaces import xmpfaces

    cm: str = lambda s: colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Fore.RESET
    cg: str = lambda s: colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Fore.RESET

    print('Тест на первоначальную инициализацию')
    # for params in [
    #     {},
    #     {'json_file': '', 'dirs': [Path('testpict'), ], 'mask': ['jpg', 'json', ]},
    #     {'json_file': 'myjson'},
    #     {'json_file': 'my.JSON'},
    #     {'json_file': 'mysave.save'},
    #     ]:
    #     fs = FacesStore(**params)
    #     print(params, f' --> json_file={cg(str(fs.json_file))}')
    #
    # print('Тест на .dirs и  .files')
    # path = 'testpict'
    # # path = r's:\MyMedia\Фото'
    # fs = FacesStore(dirs=[Path(path), ])
    # # fs = FacesStore()
    # # print('Создали объект...')
    # # fs.get_dirs(dirs=[Path(path), ])
    # for d, files in fs.dirs.items():
    #     print(d, cg(len(files)))
    #     # for f in files:
    #     #     print(Path(d) / f)
    # print(f'Директорий {cm(len(fs.dirs))} файлов {cm(len(fs.files))}')
    # print()

    # print('Тест на short_list')
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

    # dirs, local = ([Path(r's:\MyMedia\Фото\Друзья\00000000 Гараж и баня у Андрюхи')], False)
    dirs, local = ([Path(r'testpict')], False)
    json_file = 'exif.json'
    fs = FacesStore(dirs=dirs, local=local, json_file=json_file)
    print(
        f'Всего {cm(len(fs.files))} в {cm(dirs)} {"с поддиректориями" if not local else ""} в {cm(len(fs.dirs))} директориях')
    for cur_dir, files_in_dir in fs.dirs.items():
        for photo in files_in_dir:
            pil_photo = Image.open(Path(cur_dir) / Path(photo))
            faces = xmpfaces(pil_photo)
            if faces:
                fs.add_data(method=Method.EXIF,
                            dir=cur_dir,
                            file=photo,
                            data={
                                'width': pil_photo.width,
                                'height': pil_photo.height,
                            }, faces=faces)
        print(f'{cm(len(files_in_dir))} файлов в {cur_dir}: {short_list(files_in_dir, )}')
    fs.save(description='Сборная солянка, второй полет')

    ps = FacesStore.load(json_file=json_file)
    print(f'\nЗагрузка данных из {json_file}\nИмя программы {ps.program_name}\nМетоды {ps.methods}')
    for cur_dir, photofiles in ps.photos.items():
        print(cur_dir)
        for file_name, photofile in photofiles.items():
            print(f'\t{file_name} {photofile.width}*{photofile.height} лиц {len(photofile.faces_exif)}',
                  ','.join([f.name for f in photofile.faces_exif]))
    for dir, file in [
        (r'S:\dev\pytondev\printscreenscr\testpict', r'IMG_5590.jpg'),
        (r'S:\dev\pytondev\printscreenscr\testpict\Гараж', r'IMG_8731.JPG'),
        ]:
        pp = ps.photos[dir][file]
        print(f'\n{" Информация fc: ":-^80}\n{"Директория":14}: {cm(dir)}\n{"Файл":14}: {cm(file)}'
              f'\n{"Размер":14}: {cm(pp.width)}✲{cm(pp.height)}\n{"Найдено лиц":14}: {cm(len(pp.faces_exif))}')
        for f in pp.faces_exif:
            print(f'\t{cm("🤠")} {f.name:25} x: {f.x:6.4f}   y: {f.y:6.4f}   w: {f.w:6.4f}   h: {f.h:6.4f}'
                  f'   x1: {f.x1:4}   y1: {f.y1:4}   x2: {f.x2:4}   y2: {f.y2:4}')

    print(cg('Done'))
