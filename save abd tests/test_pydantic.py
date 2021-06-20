from enum import IntFlag
from random import choice
from pydantic import BaseModel
from pathlib import Path


class Tag(BaseModel):
    tagid: int
    tag: str = None
    optional: int = 100


class Method(IntFlag):
    """ Флаги методов распознования """
    EXIF = 1
    FACE_RECOGNITION = 2
    CV2 = 4
    DLIB = 8
    MTCNN = 16


class User(BaseModel):
    name: str
    method: Method = None
    tags: list[Tag] = None


print('Тест на pydantic')
jsontag1 = """
    
"""
t1 = Tag(tagid=1, tag='Одын')
t2 = Tag(tagid=2, tag='Дыва', optional=200)
random_method = choice(list(Method)) | choice(list(Method))
u = User(name='Женя', method=random_method, tags=[t1, t2, Tag.parse_raw('{"tagid": 5, "tag": "Встроенный"}')], )
print(u.dict())
if u.method & Method.EXIF:
    print('Ура! EXIF!!!')
Path('user.json').write_text(u.json(indent=2, ensure_ascii=False), encoding='utf-8')

ulka = User.parse_file(Path('user.json'))
ulka.name = 'Юлька, копия - изменено после валидации'
del ulka.tags[-1]
ulka.method = Method.DLIB | Method.FACE_RECOGNITION
print(ulka.dict())
json_info = """
{
  "name": "Вася Пупкин",
  "tags": []
}
"""
u_emptytags = User.parse_raw(json_info)
print(u_emptytags.dict())

print('Done')
