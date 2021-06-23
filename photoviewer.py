#!/usr/bin/env python
"""
Просмоторщик фотографий
"""
import PySimpleGUI as sg
# from PIL import Image, ExifTags
# import io
import pathlib
from folderphoto import FolderPhoto
# import facesstore

folder = 'testpict'
ps = FolderPhoto(folder)
lcol = [
    [sg.Listbox(values=ps.dirs, enable_events=True, size=(20, 10), font=('default', 10, 'bold'),
                tooltip='Поддиректории', key='-DIRECTORIES-')],
    [sg.Listbox(values=ps.photos, enable_events=True, size=(20, 20), key='-PHOTOS-')],
]
rcol = [[sg.Image(data=ps.get_img_data(), key='-IMAGE-')]]
layout = [[sg.Column(lcol, vertical_alignment='top'), sg.Column(rcol)]]
window = sg.Window('Image Browser: ' + ps.status(), layout, return_keyboard_events=True,
                   location=(0, 0), use_default_focus=False, resizable=True, finalize=True)
window.maximize()

while True:
    event, values = window.read()
    # print(event, values)
    if event in (sg.WIN_CLOSED, 'Escape:27'):
        break
    elif event in ('Right:39',):
        ps.next_img()
    elif event in ('Left:37',):
        ps.prev_img()
    elif event == '-PHOTOS-':  # клик по списку файлов
        ps.refresh(ps.get_num_by_name(values['-PHOTOS-'][0]))
    elif event in ('-DIRECTORIES-', 'BackSpace:8'):  # клик по списку директорий
        if event == 'BackSpace:8':  # folder up, eq '..' in list
            new_dir = '..'
        else:
            new_dir = values['-DIRECTORIES-'][0]
        new_folder = str(pathlib.Path(ps.folder) / new_dir)
        ps = FolderPhoto(new_folder)
        window['-PHOTOS-'].update(values=ps.photos)
        window['-DIRECTORIES-'].update(values=ps.dirs)
    else:
        pass
    if ps.need_refresh:
        window.set_title('Image Browser: ' + ps.status())
        window['-PHOTOS-'].update(set_to_index=ps.num)
        window['-IMAGE-'].update(data=ps.get_img_data())
        ps.need_refresh = False
window.close()
