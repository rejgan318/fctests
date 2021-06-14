import argparse
import pathlib
import face_recognition
import PIL
import pickle

SCAN_PHOTOS_FILE_NAME = "scanphotos.fr"

def get_params():
    """
    Обработка параметров одной из стандартных библиотек
    :return: параметры командной строки, объект
    """
    parcer = argparse.ArgumentParser(description='Просмотр фотографий или изображений')
    parcer.add_argument('dirs', type=str, help='Директория с файлами просмотра или имя файла')
    return parcer.parse_args()


# args = get_params()
# dirs = pathlib.Path(args.dirs)
# directories = [x for x in dirs.glob('**/*') if x.is_dir()]
# # files = [x for x in dirs.glob('**/*.jpg') if x.is_file()]
# num = 1
# for d in directories:
#     files = [x for x in d.glob('*.jpg') if x.is_file()]
#     fs = sum(f.stat().st_size for f in files)
#     print(f"{d}: файлов {len(files)} размер {fs/1024/1024:.1f}MB Переименовываем...", end='')

photos_path = pathlib.Path("testpict")
# impath = pathlib.Path(r"..\scrapered_pictures\done1")
scan_photos = [x for x in photos_path.glob('*.jpg') if x.is_file()]

face_locations = []
for photo in scan_photos:
    fi = face_recognition.load_image_file(photo)
    dump_file_fl = photo.with_suffix('.fl')
    if dump_file_fl.exists():
        with open(dump_file_fl, 'rb') as f:
            fl = pickle.load(f)
    else:
        fl = face_recognition.face_locations(fi)
        with open(dump_file_fl, 'wb') as f:
            pickle.dump(fl, f)
    dump_file_fe = photo.with_suffix('.fe')
    if dump_file_fe.exists():
        with open(dump_file_fe, 'rb') as f:
            fe = pickle.load(f)
    else:
        fe = face_recognition.face_encodings(fi)
        with open(dump_file_fe, 'wb') as f:
            pickle.dump(fe, f)
    # fr = face_recognition.face_locations(fi, number_of_times_to_upsample=0, model="cnn")
    if len(fl):
        face_locations.append({'name': str(photo), 'fr': fl})
        print(f'{photo.name} : {len(fl)}')

        # top, right, bottom, left = fr[0]
        # face_image = fi[top:bottom, left:right]
        # pil_image = PIL.Image.fromarray(face_image)
        # pil_image.show()
print("Done!")