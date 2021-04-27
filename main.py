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
import sys
import math
import pathlib


# папка для поиска
dir_with_files = r'd:\temp\exp1'  # os.path.normpath(dir_with_files))

# количество баз в папке
db_quantity_in_dir = 5

# расширения файлов для поиска
extension_list = ('rar', 'zip', 'dt', '7z')

# почта на которую отправится алерт
email_alert = 'noook@yandex.ru'

# переменная для
average_size_file_in_dir = 0


# функция не моя, взял с инета из SOF
def human_read_format(size):
    pwr = math.floor(math.log(size, 1024))
    suff = ["Б", "КБ", "МБ", "ГБ", "ТБ", "ПБ", "ЭБ", "ЗБ", "ЙБ"]
    if size > 1024 ** (len(suff) - 1):
        return "не знаю как назвать такое число :)"
    return f"{size / 1024 ** pwr:.0f}{suff[pwr]}"

# функция для определения и удаления "лишних" файлов в папке
def del_arc_files(folder_value, files_value):
    # смена текущей папки для поиска файла
    os.chdir(folder_value)
    print()

    if len(files_value) > db_quantity_in_dir-1:
        for file in files_value:
            print(' '*3, file, end=' ')
            print(os.path.join(folder_value, file), end=' ')

            print('размер файла',
                  human_read_format(os.stat(os.path.join(folder_value, file)).st_size),
                  'и в байтах =',
                  os.stat(os.path.join(folder_value, file)).st_size,
                  end=' '
                  )

            if os.stat(file).st_size > 0:
                print(' '*6, '--- удаляю файл', file)  # TODO сделать удаление файла
    else:
        print(f'_в папке {folder_value} файлов {len(files_value)} штук')


# функция для поиска файлов в исходной папке
def search_files(dir_value):
    for folders, dirs, files in os.walk(dir_value):
        del_arc_files(folders, files)

# -------------------------------------------------------- #
# новая модная фигня как запускать прогу
if __name__ == '__main__':
    search_files(dir_with_files)


