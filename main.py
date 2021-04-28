# TODO
# сделать прогу которая ходит по папкам и смотрит чтобы
# 1) в папке не было больше 5 файлов заархивированной базы
# 2) проверяет наличие свободного места и пишет письмо, если место кончается
# 3) закрывала процессы winrar в памяти
# План:
# 1) сделать функцию поиска папки с файлами
# 2) если в папке только файлы, то какие:
# 3) если размеры архивов примерно одинаковы И расширения одинаковы И начало названий файлов одинаковые,
#     то оставить последние 5 по дате
#     иначе удалить
# 4) проверить место на диске из папки root_dir_with_files
# 5) отправить письмо на ящик с инфой
#     а) сколько места на диске
#     б) логи после удаления

import os
import math
import time

# папка для поиска
root_dir_with_files = r'd:\temp\exp1'

# количество баз в папке
quantity_files_in_dir = 5

# расширения файлов для поиска
extension_list = ('rar', 'zip', 'dt', '7z')

# почта на которую отправится алерт
email_alert = 'noook@yandex.ru'

# переменная для
average_size_file_in_dir = 0


# функция не моя, взял с инета
def human_read_format(size_file):
    sizeF_human_read_format = 0
    if size_file != 0:
        pwr = math.floor(math.log(size_file, 1024))
        suff = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ', 'ПБ', 'ЭБ', 'ЗБ', 'ЙБ']
        if size_file > 1024 ** (len(suff) - 1):
            return 'не знаю как назвать такое число :)'
        sizeF_human_read_format = f'{size_file / 1024 ** pwr:.0f}{suff[pwr]}'
    return sizeF_human_read_format


def kill_proc_winrar():
    pass


def count_max_name_files(files_value):
    max_name_file = 0
    for file in files_value:
        if max_name_file < len(file):
            max_name_file = len(file)
    return max_name_file


# функция для определения и удаления "лишних" файлов в папке
def del_arc_files(folder_value):
    for folders, dirs, files in os.walk(folder_value):
        # смена текущей папки для поиска файла
        os.chdir(folders)

        max_space = count_max_name_files(files)

        if len(files) > quantity_files_in_dir:
            print()
            print(folders)

            for file in files:
                print(' ' * 3, file, '.' * (max_space - len(file)),
                      ' ... размер = ', human_read_format(os.stat(os.path.join(folders, file)).st_size),
                      ' ... в байтах = ', os.stat(os.path.join(folders, file)).st_size,
                      ' ... дата = ', time.ctime(os.stat(os.path.join(folders, file)).st_ctime),
                      end=' ', sep=''
                      )

                # TODO сделать удаление файла через try - except
                if os.stat(file).st_size == 0:
                    print(' ' * 4, '!!! файл нулевой длины !!! точно удаляю')
                elif os.stat(file).st_size > 10485760:
                    print(' ' * 4, '--- файл больше 10 МБ')
                else:
                    print(' ' * 4, '--- надо подумать')


# -------------------------------------------------------- #
# новая модная фича как запускать прогу
if __name__ == '__main__':
    kill_proc_winrar()  # удаляю зависшие процессы winrar
    del_arc_files(root_dir_with_files)  # ищу и удаляю "лишние файлы"
