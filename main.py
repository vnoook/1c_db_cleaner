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
import shutil

# папка для поиска
root_dir_with_files = r'd:\temp\exp1'

# количество баз в папке
quantity_files_in_dir = 5

# расширения файлов для поиска
extension_list = ('.rar', '.zip', '.dt', '.7z')

# почта на которую отправится алерт
email_alert = 'noook@yandex.ru'

# переменная для
average_size_file_in_dir = 0


# функция не моя, взял с инета
def human_read_format(size_file):
    size_file_human_format = 0
    if size_file != 0:
        pwr = math.floor(math.log(size_file, 1024))
        suff = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ', 'ПБ', 'ЭБ', 'ЗБ', 'ЙБ']
        if size_file > 1024 ** (len(suff) - 1):
            return 'не знаю как назвать такое число :)'
        size_file_human_format = f'{size_file / 1024 ** pwr:.0f}{suff[pwr]}'
    return size_file_human_format


# для удаления процессов winrar в памяти
def kill_proc_winrar():
    pass


# подсчёт самого длинного названия файла
def count_max_name_files(files_value):
    max_name_file = 0
    for file in files_value:
        if max_name_file < len(file):
            max_name_file = len(file)
    return max_name_file


# расчёт места на диске
def free_space_disk(folder_value):
    total_space, used_space, free_space = shutil.disk_usage(folder_value)
    return human_read_format(free_space)


# функция для определения и удаления "лишних" файлов в папке
def del_arc_files(folder_value):
    for folders, dirs, files in os.walk(folder_value):
        # смена текущей папки для поиска файла
        os.chdir(folders)

        # поиск самого длинного имени в папке
        max_space = count_max_name_files(files)

        # нужно ли выводить название папки или нет, если в папке нет файлов с расширением из extension_list
        flag_exist_ext = False
        for file in files:
            if not flag_exist_ext:
                if os.path.splitext(file)[1] in extension_list:
                    print()
                    print(folders)
                    flag_exist_ext = True

        for file in files:
            if os.path.splitext(file)[1] in extension_list:
                print(' '*3, file, '.'*(max_space - len(file)),
                      ' ... размер = ', human_read_format(os.stat(os.path.join(folders, file)).st_size),
                      ' ... в байтах = ', os.stat(os.path.join(folders, file)).st_size,
                      ' ... дата = ', time.ctime(os.stat(os.path.join(folders, file)).st_ctime)
                      # end=' ', sep=''
                      )

                # if os.stat(file).st_size < 1048576:
                #     print(' '*4, '!!! файл малой длины - удаляю !!!')
                #     try:
                #         os.remove(file)
                #         print(' '*4 + '_'*50 + f'Файл {file} удалён')
                #     except PermissionError as errorPE:
                #         print(' '*4 + '_'*50 +
                #               f'Ошибка: нет доступа для удаления файла {errorPE.filename} - {errorPE.strerror}'
                #               )
                #     except FileNotFoundError as errorFNFE:
                #         print(' '*4 + '_'*50 + f'Ошибка: файл не найден {errorFNFE.filename} - {errorFNFE.strerror}')
                #     else:
                #         pass
                #     finally:
                #         pass
                # elif os.stat(file).st_size > 10485760:
                #     print(' '*4, '--- файл больше 10 МБ')
                # else:
                #     print(' '*4, '--- надо подумать')

        # if len(files) > quantity_files_in_dir:


# новая модная фича как запускать прогу
if __name__ == '__main__':
    kill_proc_winrar()  # удаляю зависшие процессы winrar
    del_arc_files(root_dir_with_files)  # ищу и удаляю "лишние файлы"

    print()
    print(free_space_disk(root_dir_with_files))
