# TODO
'''
сделать прогу которая ходит по папкам и смотрит чтобы
1) в папке не было больше 5 версий заархивированной базы
2) проверяет наличие свободного места и пишет письмо, если место кончается
'''

import os
import pathlib
import sys

# папка для поиска
dir_for_clean = r'd:\temp\exp1'

# количество баз в папке
db_quantity_in_dir = 5

# почта на которую отправится алерт
email_alert = 'noook@yandex.ru'


if __name__ == '__main__':
    print(dir_for_clean)








# os.path.dirname(path1)
# os.path.realpath(path1)
# os.getcwd().__iter__()
# os.fspath(path1)
# os.path.abspath(name_file)
# os.path.basename(name_file)
# os.path.normpath(name_file)





