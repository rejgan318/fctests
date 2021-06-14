import pickle
import pprint
import argparse
import pathlib
import json

ap = argparse.ArgumentParser(description='Просмотр pickle-файла')
ap.add_argument('pickle_file', type=str, nargs=1, help='picle-файл', )
pars = ap.parse_args('photos.pickle'.split())
pickle_file = pars.pickle_file[0]

print('Анализ', pickle_file)
with open(pickle_file, 'rb') as f:
    info = pickle.load(f)
pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(info)

print(type(info))
if type(info) == list:
    print('Список', len(info))
elif type(info) == dict:
    print('Словарь с ключами', info.keys())

if type(info[0]) == dict:
    print('Ключи элемента:', info[0].keys())

# for photo in info:
#     print(f'{photo["n"]:3} {photo["photo"]:30} {len(photo["exif"]):3} {len(photo["fc"]):3} {len(photo["cv2"]):3}')
print()
# dirs_photos = {}
# for i in range(len(info)):
#     photo = info[i]['photo']
#     d_photo = str(pathlib.Path(photo).parent)
#     n_photo = str(pathlib.Path(photo).name)
#     if dirs_photos.get(d_photo, False):
#         dirs_photos[d_photo].append(info[i])
#     else:
#         dirs_photos[d_photo] = [info[i]]
#
# for dirs, to_save in dirs_photos.items():
#     dir_to_save = pathlib.Path(dirs) / 'photos.pickle'
#     # dir_to_save = pathlib.Path(to_save[0]['photo']).parent
#     print(dirs, len(to_save), 'файлов в', dir_to_save )
