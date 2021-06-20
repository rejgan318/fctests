"""
Тесты на многопоточность
    - argparse: парсинг необязательного списка и опции
 - получить параметр - имя дирктории или файла (может быть несколько, вперемежку).Если не задан - текущая директория
 - в зависимости от полученного парамера -local учитывать поддииректории или нет
 - вывести в файл 'filesjpg.csv' все файлы .jpg в указанной директории и поддиректориях
 - считать из csv-файла и вывести в красивом виде с помощью prettytable
"""
import pathlib
import argparse
import multiprocessing
import queue
import PIL
import face_recognition
import cv2
import pickle
import json
from tqdm import tqdm
import xmpfaces         # Мое
import facesstore       # Мое
# import mtcnn


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


def save_pickle(filename, data):
    with open(filename, 'wb') as f:
        pickle.dump(data, f)


def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def dump_all_data(save_list):
    """  Весь список полученных данных сохранить по частям в соответствующих деректориях """

    dirs_photos = {}   # рабочий словарь с ключом имя-директории и данными для сохранения
    for i in range(len(save_list)):
        photo = save_list[i]['photo']
        d_photo = str(pathlib.Path(photo).parent)
        if dirs_photos.get(d_photo, False):
            dirs_photos[d_photo].append(save_list[i])
        else:
            dirs_photos[d_photo] = [save_list[i]]

    for dirs, to_save in dirs_photos.items():
        fs = facesstore.FaceInfo('photos_fs.json', str(pathlib.Path(dirs)))

        save_pickle(str(pathlib.Path(dirs) / 'photos.pickle'), to_save)
        save_json(str(pathlib.Path(dirs) / 'photos.json'), to_save)


def get_exif_list(photos: list[pathlib.Path]) -> list:
    """
    Для каждого файла из списка получить из exif отмеченные лица
    :param photos: список файлов в формате pathlib.Path
    :return: общий список лиц
    """
    exif_list = []
    # for photo in photos:
    for i in tqdm(range(len(photos)), desc='Exif'):
        photo = photos[i]
        pil_photo = PIL.Image.open(str(photo))
        faces, wh = xmpfaces.xmpfaces(pil_photo)
        exif_list.append(faces)
        # exif_list.append([faces, wh])
    return exif_list


def get_fc(tasks_run, tasks_done):
    """
    Мультипроцессорная молоьилка, один экземпляр из нескольктх возможных по числу ядер
    Если есть задача в очереди задач,
        получаем параметры задачи
        выполняем необходимое
        результаты помещаем результат в очередь результатов
    если очередб задач на выполнение пуста - выходим, закрывая этот экземпляр молотилки, процесс заканчивается
    :param tasks_run: очередь задач на выполнение
    :param tasks_done: выходная очередь задач результатов
    :return: -
    """
    while True:
        try:
            i, photo = pickle.loads(tasks_run.get_nowait())
        except queue.Empty:
            break
        else:
            # print('Обрабатывается', i, photo)
            im_photo = face_recognition.load_image_file(str(photo))
            faces = face_recognition.face_locations(im_photo)
            tasks_done.put(pickle.dumps((i, faces)))
            # print("Готово", i)
    return True


def get_fc_list(photos: list) -> list:

    number_of_task = len(photos)
    tasks_run = multiprocessing.Queue()
    # Формируем список параметров для каждой задачи
    for i in range(number_of_task):
        tasks_run.put(pickle.dumps([i, str(photos[i])]))

    # Запускаем процессы
    tasks_done = multiprocessing.Queue()    # здесь будут результаты по каждой задаче
    processes = []
    number_of_processes = multiprocessing.cpu_count()   # по максимуму
    for i in range(number_of_processes):
        p = multiprocessing.Process(target=get_fc, args=(tasks_run, tasks_done))
        processes.append(p)
        p.start()

    # заготовка для индексного заполнения. Задачи могут выполняться не в порядке их запуска
    fc_list = [None] * len(photos)
    for t in tqdm(range(number_of_task), desc='fc  '):   # прогресс-бар для красоты
        while tasks_done.empty():   # Ждем результата хотя бы одной выполненной задачи
            pass
        i, faces = pickle.loads(tasks_done.get())   # результат в нормальном питоновском виде
        fc_list[i] = faces  # созраняем

    # t = 0
    # while t < number_of_task:
    #     if not tasks_done.empty():
    #         i, faces = pickle.loads(tasks_done.get())
    #         fc_list[i] = faces
    #         if len(faces):
    #             print(f'{i:3} {str(photos[i]):30} {len(faces)}')
    #         t += 1

    # Дождаться выполнения всех зажач, синхронное окончание всех процессов
    # for p in processes:
    #     p.join()
    # когда все задачи закончены, просто получим результаты из очереди
    # while not tasks_done.empty():
    #     i, faces = pickle.loads(tasks_done.get())
    #     fc_list[i] = faces
    #     print(photos[i], ' ', end='')
    #     # print('Получено: i =', i, 'faces =', faces)

    return fc_list


def get_fc_list_nomp(photos: list) -> list:
    fc_list = []
    for photo in photos:
        im_photo = face_recognition.load_image_file(str(photo))
        faces = face_recognition.face_locations(im_photo)
        print(photo)
        fc_list.append(faces)
    return fc_list


def get_cv2_list(photos):
    face_cascade_name = 'data/haarcascades/haarcascade_frontalface_alt.xml'
    face_cascade = cv2.CascadeClassifier()
    # if not face_cascade.load(cv2.samples.findFile(face_cascade_name)):
    if not face_cascade.load(face_cascade_name):
        print('--(!)Error loading face cascade')
        exit(0)

    fc_list = []
    # for i, photo in enumerate(photos):
    for i in tqdm(range(len(photos)), desc='cv2 '):
        photo = photos[i]
        imgcv = cv2.imread(str(photo))
        frame_gray = cv2.cvtColor(imgcv, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        faces = face_cascade.detectMultiScale(frame_gray)
        # print(f'{i:3} {str(photo):30} {len(faces)}')
        fc_list.append([x.tolist() for x in faces])
        # cv.imshow('Capture - Face detection', )

    return fc_list


# def get_mtcnn_list(photos):
#
#     fc_list = []
#     # for i, photo in enumerate(photos):
#     detector = mtcnn.MTCNN()
#     for i in tqdm(range(len(photos)), desc='mtcn'):
#         photo = photos[i]
#         img = cv2.imread(str(photo))
#         faces = detector.detect_faces(img)
#         # print(f'{i:3} {str(photo):30} {len(faces)}')
#         fc_list.append(faces)
#
#     return fc_list
def main():

    ap = argparse.ArgumentParser(description='Список всех jpg в файл')
    ap.add_argument('directory', type=str, nargs='*', default='.', help='Спикок директорий с jpg. По умолчанию текущая', )
    ap.add_argument('--local', '-l', default=False, action='store_true',
                    help='Без вложенных директорий. По умолчанию с поддиректориями', )
    pars = ap.parse_args('testpict'.split())
    # pars = ap.parse_args('../scrapered_pictures/done1'.split())

    # jpg_list = get_files_by_mask(pars.directory, local=pars.local)
    # # num_cpu = multiprocessing.cpu_count()
    # # print("Ядер на этом компьютере:", num_cpu, )
    # print(f'Директории {pars.directory} Количество задач  (файлов) для обработки:{len(jpg_list)}')
    #
    # fs = facesstore.FacesStore(file_name='fs1', path='.')
    # exif_list = get_exif_list(jpg_list)
    # # fc_list = get_fc_list(jpg_list)
    # # cv2_list = get_cv2_list(jpg_list)
    #
    # save_list = []
    # for i, photo in enumerate(jpg_list):
    #     # print(f'{i:3} {str(photo):30} {len(exif_list[i]):3} {len(fc_list[i]):3} {len(cv2_list[i]):3} ')
    #     save_list.append({
    #         'n': i,
    #         'photo': str(photo),
    #         'exif': exif_list[i],
    #         # 'fc': fc_list[i],
    #         # 'cv2': cv2_list[i],
    #     })
    #
    # dump_all_data(save_list)

    photos_list = facesstore.get_files_by_mask(pars.directory, local=pars.local)
    print(f'Всего {facesstore.cm(len(photos_list))} в {facesstore.cm(pars.directory)} {"с поддиректориями" if not pars.local else ""} ')
    for cur_dir, files_in_dir in facesstore.get_dirs(photos_list).items():
        fs = facesstore.FacesStore('mystore', cur_dir)
        print(f'{facesstore.cm(len(files_in_dir))} файлов в {cur_dir}: {facesstore.short_list(files_in_dir, )}')
        exif_list = get_exif_list([pathlib.Path(cur_dir) / pathlib.Path(p) for p in files_in_dir])
        fs.add_data(data=dict(zip(files_in_dir, exif_list)), method=facesstore.Method.EXIF)
        fs.save()

    print('Done.')
    return True


if __name__ == '__main__':
    main()
