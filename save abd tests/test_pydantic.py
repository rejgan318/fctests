from pydantic import BaseModel
from pathlib import Path

class Tag(BaseModel):
    tagid: int
    tag: str = None
    optional: int = 100


class JastTag():
    tagid: int
    tag: str = None
    optional: int = 100


class User(BaseModel):
    name: str
    method: int
    tags: list[Tag]


print('Тест на pydantic')
jsontag1 = """
    {"tagid": 5, "tag": "Новый"}
"""
t1 = Tag(tagid=1, tag='Одын')
t2 = Tag(tagid=2, tag='Дыва', optional=200)
t3 = Tag.parse_raw(jsontag1)
u = User(name='Женя', method=55, tags=[t1, t2, t3])
Path('user.json').write_text(u.json(indent=2, ensure_ascii=False), encoding='utf-8')

ulka = User.parse_file(Path('user.json'))
ulka.name = 'Юлька'

print('Done')
