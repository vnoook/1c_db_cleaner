# TODO
# сделать прогу которая ходит по папкам и смотрит чтобы
# 1) в папке не было больше 5 версий заархивированной базы
# 2) проверяет наличие свободного места и пишет письмо, если место кончается
#
# План:
# 1) сделать функцию поиска папки с файлоами
# 2) если в папке только файлы, то какие
# 3) если размеры архивов примерно одинаковы И расширения одинаковы И начало названий файлов одинаковые,
#     то оставить последние 5 по дате
# 4) проверить место на диске из папки dir_with_files
# 5) отправить письмо на ящик с инфой
#     а) сколько места на диске
#     б) логи после удаления

import os
# import pathlib
# import sys

# папка для поиска
dir_with_files = r'd:\temp\exp1'  # os.path.normpath(dir_with_files))

# количество баз в папке
db_quantity_in_dir = 5

# расширения файлов для поиска
extension_list = ('rar', 'zip', 'dt', '7z')

# почта на которую отправится алерт
email_alert = 'noook@yandex.ru'

average_size_file_in_dir = 0


def get_list_dirs():
    pass


def get_arc_files():
    pass


def del_arc_files():
    pass


def search_files(dir_value):
    for folders, dirs, files in os.walk(dir_value):
        print()
        print(folders)
        print(dirs)
        print(files)

# -------------------------------------------------------- #
if __name__ == '__main__':
    search_files(dir_with_files)
