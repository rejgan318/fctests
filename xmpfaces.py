import xml.etree.ElementTree as ET

# пространство имен для парсинга xmp
NS_DICT = {
    'x': 'adobe:ns:meta/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'mwg-rs': 'http://www.metadataworkinggroup.com/schemas/regions/',
    'stArea': 'http://ns.adobe.com/xmp/sType/Area#',
    'stDim': 'http://ns.adobe.com/xap/1.0/sType/Dimensions#',
}


def ns_key(ns_name: str, symbolic_name: str, ns_dict=None) -> str:
    """
    Сформировать ключ атрибута, учитывая пространство имен
    :param ns_name: пространство имен
    :param symbolic_name: символическое имя атрибута
    :param ns_dict: словарь пространств
    :return: сформированный ключ типа такого '{http://www.metadataworkinggroup.com/schemas/regions/}name'
    """
    if ns_dict is None:
        ns_dict = NS_DICT
    return f'{{{ns_dict[ns_name]}}}{symbolic_name}'


def get_xmp(pil_im) -> str:
    """
    Получить из объекта типа PIL.Image xmp сектицию в виде xml-разметки
    :param pil_im:
    :return: строка utf-8, содержащая xmp в xml-формате
    """
    SEGMENT = 'APP1'
    MARKER = b'http://ns.adobe.com/xap/1.0/'

    if not hasattr(pil_im, 'applist'):
        return None
    for segment, content in pil_im.applist:
        try:
            marker, body = content.split(b'\x00', 1)
        except ValueError:
            return None
        # marker, body = content.split(b'\x00', 1)
        if segment == SEGMENT and marker == MARKER:
            return str(body.decode('utf-8'))


def get_face_rect(xywh: tuple[float, float, float, float], im_wh: tuple[int, int], rotate: int = None)\
        -> tuple[int, int, int, int]:
    """
    Сервисная функция. Полезная для получения абсолютных координат прямоугольника лица после масштабирования
    по заданным нормализованным координатам центра xy размером wh (xywh). Учитывается возможный поворот,
    если указана ориентация
    :param xywh: нормализованные координаты центра и размеры прямоугольника (обычно из Exif)
    :param im_wh: размеры в пикселях отображаемого изображения, для которого нужно вычислить абсолютные координаты углов
    :param rotate: None | 3 | 6 | 8 - ориентация из exif - нет | 180 | 270 | 90
    :return: абсолютные координаты прямоугольника лица на изображении с размерами im_wh
    """
    ROTATE_180, ROTATE_270, ROTATE_90 = 3, 6, 8
    x, y, w, h = xywh
    imw, imh = im_wh
    # при повороте не меняются размеры, только координаты центра прямоугольника
    if rotate == ROTATE_180:
        x = 1 - x
        y = 1 - y
    elif rotate == ROTATE_270:
        x, y = y, x
    elif rotate == ROTATE_90:
        x = 1 - y
        y = 1 - x
    x1 = int(imw * (x - w / 2))
    y1 = int(imh * (y - h / 2))
    x2 = int(imw * (x + w / 2))
    y2 = int(imh * (y + h / 2))
    return x1, y1, x2, y2


def get_faces(xml_xmp: str) -> list[dict]:
    faces = []
    # parser = ET.XMLParser(encoding="utf-8")
    # tree = ET.fromstring(xml_xmp, parser=parser)
    tree = ET.fromstring(xml_xmp)
    # print(f'Размеры: w={im_w}, h={im_h}')
    xml_regions = tree.find('rdf:RDF/rdf:Description/mwg-rs:Regions', namespaces=NS_DICT)
    if not xml_regions:
        return []
    xml_faces = xml_regions.findall('mwg-rs:RegionList/rdf:Bag/rdf:li', namespaces=NS_DICT)
    xml_applied_to_dimensions = xml_regions.find('mwg-rs:AppliedToDimensions', namespaces=NS_DICT)
    im_w = int(xml_applied_to_dimensions.get(ns_key('stDim', 'w')))
    im_h = int(xml_applied_to_dimensions.get(ns_key('stDim', 'h')))

    for xml_face in xml_faces:
        xml_face_description = xml_face.find('rdf:Description', namespaces=NS_DICT)

        face = {}
        face['name'] = xml_face_description.get(ns_key('mwg-rs', 'Name'), None)
        face['type_region'] = xml_face_description.get(ns_key('mwg-rs', 'Type'), None)
        rotation = xml_face_description.get(ns_key('mwg-rs', 'Rotation'), None)
        if rotation:
            face['rotation'] = float(rotation)

        xml_area = xml_face_description.find('mwg-rs:Area', namespaces=NS_DICT)
        # относительные нормированные коорднаты центроы областей и размеры
        face['h'] = float(xml_area.get(ns_key('stArea', 'h')))
        face['w'] = float(xml_area.get(ns_key('stArea', 'w')))
        face['x'] = float(xml_area.get(ns_key('stArea', 'x')))
        face['y'] = float(xml_area.get(ns_key('stArea', 'y')))
        # абсолютные координаты в пикселях
        face['x1'], face['y1'], face['x2'], face['y2'] = get_face_rect(xywh=(face['x'], face['y'], face['w'], face['h']),
                                                                       im_wh=(im_w, im_h))
        faces.append(face)
    return faces


def xmpfaces(image) -> list[dict]:
    """
    Основная функция модуля
    :param image: PIL-Image
    :return: список словарей с информацияей о помеченных областях на фотографии
    """
    xml_xmp = get_xmp(image)
    return get_faces(xml_xmp) if xml_xmp else []


# ----------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    import pathlib
    from PIL import Image, ExifTags
    import colorama
    from facesstore import get_files_by_mask, get_dirs, short_list, FacesStore, Method
    # import facesstore

    cm: str = lambda s: colorama.Fore.LIGHTMAGENTA_EX + str(s) + colorama.Fore.RESET
    cg: str = lambda s: colorama.Fore.LIGHTGREEN_EX + str(s) + colorama.Fore.RESET

    # impil = 'testpict/Sashka/IMG_3418.JPG'
    # # impil = 'testpict/Sashka/IMG_3931.JPG'
    # im = Image.open(impil)
    #
    # exif = im._getexif()
    # orientation = 0x0112  # 274
    # if exif and exif.get('orientation', None):
    #     for exif_rotate, deegres in ((3, 180), (6, 2700), (8, 90),):
    #         if exif[orientation] == exif_rotate:
    #             im = im.rotate(deegres, expand=True)
    #             break
    # xml_xmp = get_xmp(im)
    # print(xml_xmp)


    # imdir = pathlib.Path('testpict')
    # for impil in imdir.glob('*.jpg'):
    #     if impil.is_file():
    #         im = Image.open(impil)
    #         faces, wh = xmpfaces(im)
    #         print(impil.name, faces, wh)

    # # FILE = 'img/im.jpg'
    # # FILE = 'img/1/12/IMG_5593.jpg'
    # FILE = 'testpict/IMG_5590.jpg'
    # im = Image.open(FILE)
    # faces, wh = xmpfaces(im)

    # OUTFILE = 'out.jpg'
    # draw = ImageDraw.Draw(im)
    # for face in faces:
    #     draw.rectangle([(face['x1'], face['y1']), (face['x2'], face['y2'])], width=3, outline=(0, 255, 0))
    #
    # im.save(OUTFILE, 'JPEG')
    # print(faces)
    # print(wh)
