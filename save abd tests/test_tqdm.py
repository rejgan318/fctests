""" Тест на модуль tqdm"""
import tqdm
import time

print("Поехали!")
for i in tqdm.tqdm(range(50)):
    time.sleep(0.100)
print('Ok')
