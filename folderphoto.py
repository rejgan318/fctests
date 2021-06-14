from PIL import Image, ExifTags
import io
import pathlib


class FolderPhoto:
    def __init__(self, folder_name):
        self.MASK = '*.jpg'
        self.folder = pathlib.Path(folder_name).resolve()
        self.photos = self.get_photos()
        self.dirs = self.get_dirs()
        self.count = len(self.photos)
        self.num = None    # текущий номер файла, сейчас отображается
        self.name = None
        self.img = None
        self.need_refresh: bool = True
        if len(self.photos):
            self.refresh(0)
            # self.need_refresh: bool = True

    def refresh(self, n: int):
        """ новй файл из списка. меняем имя и загружаем """
        self.num = n
        self.name = self.photos[self.num]
        self.get_img()
        self.need_refresh = True

    def get_num_by_name(self, name: str) -> int:
        return self.photos.index(name)

    def next_img(self):
        """ следующий файл циклически становится текущим """
        self.num = self.num + 1 if self.num < self.count - 1 else 0
        self.refresh(self.num)
        return

    def prev_img(self):
        """ предыдущий файл циклически становится текущим """
        self.num = self.num - 1 if self.num > 0 else self.count - 1
        self.refresh(self.num)
        return

    def get_photos(self):
        """ получить список фотографий """
        return [str(p.name) for p in pathlib.Path(self.folder).glob(self.MASK) if p.is_file()]

    def get_dirs(self):
        """ получить список поддиректорий, добавив .. """
        return ['..'] + [str(d.name) for d in pathlib.Path(self.folder).glob("*") if d.is_dir()]

    def get_img(self):
        """ загрузить файл; проверить по exif, если необходимо - повернуть; промасштабировать """
        maxsize = (1530, 850)
        self.img = Image.open(pathlib.Path(self.folder) / self.name)
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            exif = self.img._getexif()
            if exif:
                if exif[orientation] == 3:
                    self.img = self.img.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    self.img = self.img.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    self.img = self.img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            pass  # cases: image don't have getexif
        self.img.thumbnail(maxsize)

    def get_img_data(self):
        """ Вернуть img в формате png (из-за ограничений tkinter) """
        if not self.img:
            return None
        bio = io.BytesIO()
        self.img.save(bio, format="PNG")
        return bio.getvalue()

    def status(self) -> str:
        return f'  {self.num + 1}/{self.count}   ' + str(pathlib.Path(self.folder) / self.name) if self.name else ''
