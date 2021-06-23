"""
Служебный файл для photoviewer
"""
from PIL import Image, ExifTags, ImageDraw, ImageFont
import io
from pathlib import Path
import facesstore
from xmpfaces import get_face_rect, xmpfaces


class FolderPhoto:

    json_file = 'exif.json'
    faces = facesstore.FacesStore.load(json_file)
    # fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", 40)
    fnt = ImageFont.truetype("Absolut Pro Light Condensed.ttf", 14, encoding='UTF-8')
    # fnt = ImageFont.truetype("Zekton Condensed Book.ttf", 12, encoding='UTF-8')

    def __init__(self, folder_name):
        self.MASK = '*.jpg'
        self.folder = Path(folder_name).resolve()
        self.photos = self.get_photos()
        self.dirs = self.get_dirs()
        self.count = len(self.photos)
        self.num = None    # текущий номер файла, сейчас отображается
        self.name = None
        self.img = None
        self.need_refresh: bool = True
        self.maxsize = (1530, 850)
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
        return [str(p.name) for p in Path(self.folder).glob(self.MASK) if p.is_file()]

    def get_dirs(self):
        """ получить список поддиректорий, добавив .. """
        return ['..'] + [str(d.name) for d in Path(self.folder).glob("*") if d.is_dir()]

    def get_img(self):
        """ загрузить файл; проверить по exif, если необходимо - повернуть; промасштабировать """
        self.img = Image.open(Path(self.folder) / self.name)

        photo_file = self.faces.get_photo(str(self.folder), str(self.name))
        color = 'green'
        if photo_file:
            face_exif = self.faces.photos[str(self.folder)][str(self.name)].faces_exif
            if len(face_exif):
                color = 'yellow'
        else:
            face_exif = [facesstore.FaceInfo(**f) for f in xmpfaces(self.img)]

        tag_orientation = 274
        exif = self.img._getexif()
        if exif and exif.get(tag_orientation, None):
            rotate = exif[tag_orientation]
            if rotate == 3:
                self.img = self.img.rotate(180, expand=True)
            elif rotate == 6:
                self.img = self.img.rotate(270, expand=True)
            elif rotate == 8:
                self.img = self.img.rotate(90, expand=True)
        else:
            rotate = None

        self.img.thumbnail(self.maxsize)
        if len(face_exif):
            self.draw_faces(face_exif, color=color, rotate=rotate)

    def draw_faces(self, faces: list[facesstore.FaceInfo], color: str, rotate=None):
        draw = ImageDraw.Draw(self.img)
        for face in faces:
            xy = get_face_rect(xywh=(face.x, face.y, face.w, face.h), im_wh=self.img.size, rotate=rotate)
            draw.rectangle(xy, fill=None, width=1, outline=color)
            if face.name:
                draw.text((xy[0], xy[1]-14), face.name, font=self.fnt, fill=color)

    def get_img_data(self):
        """ Вернуть img в формате png (из-за ограничений tkinter) """
        if not self.img:
            return None
        bio = io.BytesIO()
        self.img.save(bio, format="PNG")
        return bio.getvalue()

    def status(self) -> str:
        return f'  {self.num + 1}/{self.count}   ' + str(Path(self.folder) / self.name) if self.name else ''
