from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
import pathlib

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


def get_faces(xml_xmp: str):
    # parser = ET.XMLParser(encoding="utf-8")
    # tree = ET.fromstring(xml_xmp, parser=parser)
    tree = ET.fromstring(xml_xmp)
    xml_regions = tree.find('rdf:RDF/rdf:Description/mwg-rs:Regions', namespaces=NS_DICT)
    xml_applied_to_dimensions = xml_regions.find('mwg-rs:AppliedToDimensions', namespaces=NS_DICT)
    im_w = int(xml_applied_to_dimensions.get(ns_key('stDim', 'w')))
    im_h = int(xml_applied_to_dimensions.get(ns_key('stDim', 'h')))
    # print(f'Размеры: w={im_w}, h={im_h}')
    xml_faces = xml_regions.findall('mwg-rs:RegionList/rdf:Bag/rdf:li', namespaces=NS_DICT)

    faces = []
    boxes = []
    for xml_face in xml_faces:
        xml_face_description = xml_face.find('rdf:Description', namespaces=NS_DICT)

        face = {}
        box = {}
        face['Name'] = xml_face_description.get(ns_key('mwg-rs', 'Name'), None)
        face['Type'] = xml_face_description.get(ns_key('mwg-rs', 'Type'), None)
        rotation = xml_face_description.get(ns_key('mwg-rs', 'Rotation'), None)
        face['Rotation'] = float(rotation) if rotation else rotation

        xml_area = xml_face_description.find('mwg-rs:Area', namespaces=NS_DICT)
        # относительные нормированные коорднаты центроы областей и размеры
        face['h'] = float(xml_area.get(ns_key('stArea', 'h')))
        face['w'] = float(xml_area.get(ns_key('stArea', 'w')))
        face['x'] = float(xml_area.get(ns_key('stArea', 'x')))
        face['y'] = float(xml_area.get(ns_key('stArea', 'y')))
        # абсолютные координаты в пикселях
        face['x1'] = int(im_w * (face['x'] - face['w'] / 2))
        face['y1'] = int(im_h * (face['y'] - face['h'] / 2))
        face['x2'] = int(im_w * (face['x'] + face['w'] / 2))
        face['y2'] = int(im_h * (face['y'] + face['h'] / 2))
        faces.append(face)
        box['hwxy'] = [face['h'], face['w'], face['x'], face['y']]
        box['x1y1x2y2'] = [face['x1'], face['y1'], face['x2'], face['y2']]
        boxes.append(box)
    return faces, (im_w, im_h)


def xmpfaces(image):
    """
    :param image: PIL-Image
    :return: список словарей с информацияей о помеченных областях на фотографии
    """
    xml_xmp = get_xmp(image)
    if xml_xmp:
        faces, wh = get_faces(xml_xmp)
    else:
        faces = []
        wh = image.size
    return faces, wh


if __name__ == '__main__' :

    imdir = pathlib.Path('testpict')
    for impil in imdir.glob('*.jpg'):
        if impil.is_file():
            im = Image.open(impil)
            faces, wh = xmpfaces(im)
            print(impil.name, faces, wh)

    # FILE = 'img/im.jpg'
    # FILE = 'img/1/12/IMG_5593.jpg'
    FILE = 'testpict/IMG_5590.jpg'
    im = Image.open(FILE)
    faces, wh = xmpfaces(im)


    OUTFILE = 'out.jpg'
    draw = ImageDraw.Draw(im)
    for face in faces:
        draw.rectangle([(face['x1'], face['y1']), (face['x2'], face['y2'])], width=3, outline=(0, 255, 0))

    im.save(OUTFILE, 'JPEG')
    print(faces)
    print(wh)
