import time
from colorama import Cursor, init, Fore

# This assumes your terminal is 80x24. Ansi minimum coordinate is (1,1).
MINY, MAXY = 1, 24
MINX, MAXX = 1, 80
pos = lambda y, x: Cursor.POS(x, y)

init()
print("Цифры по диагонали...")
for i in range(20):
    print(Cursor.POS(i+1, i+1), i+1)
    time.sleep(0.05)

print("Процентный отсчет...")
for i in range(100):
    print(f'Выполнено {Fore.LIGHTGREEN_EX}{i+1:3}{Fore.RESET}%', end='\r')
    time.sleep(0.02)

print('Ok')
print(Cursor.POS(1, 19), "++++++++++++++++++++++++++++++++++++")
time.sleep(0.5)
print(Cursor.POS(1, 44), "====================================")

# for y in range(MINY, 1 + MAXY):
#     print('%s %s ' % (pos(y, MINX), pos(y, MAXX)), end='')

