"""
Тесты
    - argparse: парсинг необязательного списка и опции
    - csv: запись в файл и чтение из файла
    - pathlib: получен список файлов в списке директорий и файлов (из параметров) с поддиректориями
    - prettytable: красивый табличный вывод
 - получить параметр - имя дирктории или файла (может быть несколько, вперемежку).Если не задан - текущая директория
 - в зависимости от полученного парамера -local учитывать поддииректории или нет
 - вывести в файл 'filesjpg.csv' все файлы .jpg в указанной директории и поддиректориях
 - считать из csv-файла и вывести в красивом виде с помощью prettytable
"""
import pathlib
import argparse
import csv
from prettytable import PrettyTable


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


ap = argparse.ArgumentParser(description='Список всех jpg в файл')
ap.add_argument('directory', type=str, nargs='*', default='.', help='Спикок директорий с jpg. По умолчанию текущая', )
ap.add_argument('--local', '-l', default=False, action='store_true',
                help='Без вложенных директорий. По умолчанию с поддиректориями', )
pars = ap.parse_args('testpict'.split())
# pars = ap.parse_args('testpict ../scrapered_pictures/done1'.split())
jpg_list = get_files_by_mask(pars.directory, local=pars.local)
print('Найдено ', len(jpg_list), ' файлов')

CSV_FILE = 'save abd tests/filesjpg.csv'
print('Созраняем в csv-файле ' + CSV_FILE)
with open(CSV_FILE, 'w', newline='') as csvfile:
    i = 1
    spamwriter = csv.writer(csvfile, delimiter=' ', quoting=csv.QUOTE_MINIMAL)
    for jpg in jpg_list:
        spamwriter.writerow([i, str(jpg)])
        # csv.write(f'{i},{str(jpg)}\n')
        i += 1

# Танцуют все! Красивый табличный вывод!
pt = PrettyTable()
col1 = '№'
col2 = 'Файл'
col3 = 'Размер'
pt.field_names = [col1, col2, col3]
pt.align[col1] = 'r'
pt.align[col2] = 'l'
pt.align[col3] = 'r'

print('Считаем из файла ранее созраненное из ' + CSV_FILE)
with open(CSV_FILE, 'r', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=' ')
    for row in spamreader:
        i = row[0]
        jpg = pathlib.Path(row[1])
        # print(f'{i:3} {str(jpg)} {jpg.stat().st_size}')
        pt.add_row([i, str(jpg), f'{jpg.stat().st_size / 1024 / 1024:5.2f}MB'])
print("Получено в лучшем виде")
print(pt)
