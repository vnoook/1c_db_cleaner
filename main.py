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
import time
import datetime
import shutil
import psutil
import math

# переменная для удаления
flag_del = False

# папка для поиска
root_dir_with_files = r'd:\temp\exp1'

# количество баз в папке
quantity_files_in_dir = 5

# расширения файлов для поиска
extension_list = ('.rar', '.zip', '.dt', '.7z')

# размер файла в байтах "минимального размера"
min_size = 10485760  # 10 Mb

# почта на которую отправится статистика работы
email_alert = 'noook@yandex.ru'


# функция не моя, взял с инета
# читаемый вид из байтов в человеческий вид
def human_read_format(size_file):
    size_file_human_format = 0
    if size_file != 0:
        pwr = math.floor(math.log(size_file, 1024))
        suff = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ', 'ПБ', 'ЭБ', 'ЗБ', 'ЙБ']
        if size_file > 1024 ** (len(suff) - 1):
            return 'не знаю как назвать такое число :)'
        size_file_human_format = f'{size_file / 1024 ** pwr:.0f}{suff[pwr]}'
    return size_file_human_format


# читаемый вид из времени в человеческий вид
def human_read_date(date_file):
    date_file_human_format = str(datetime.datetime.fromtimestamp(date_file)).split('.')[0]
    return date_file_human_format


# для удаления процессов winrar в памяти
def kill_proc_winrar():
    process_winrar = 'winrar.exe'
    for process in psutil.process_iter():
        if process.name().lower() == process_winrar:
            process.kill()


# отправка статистики работы
def send_email_stattistics():
    # TODO
    pass


# подсчёт самого длинного названия файла
def count_max_name_files(files_value):
    max_name_file = 0
    for file in files_value:
        if os.path.splitext(file)[1] in extension_list:
            if max_name_file < len(file):
                max_name_file = len(file)
    return max_name_file


# расчёт места на диске
def free_space_disk(folder_value):
    total_space, used_space, free_space = shutil.disk_usage(folder_value)
    return human_read_format(free_space)


# функция для определения и удаления "мелких" файлов в папке
def del_arc_files(folder_value):
    for folders, dirs, files in os.walk(folder_value):
        # смена текущей папки для поиска файла
        os.chdir(folders)

        # поиск самого длинного имени в папке
        max_space = count_max_name_files(files)

        # количество файлов из extension_list и удалённых файлов
        count_arc_files = 0
        count_del_files = 0

        # список для файлов больше минимального размера
        list_big_files = []

        # нужно ли выводить название папки или нет, если в папке нет файлов с расширением из extension_list
        flag_exist_ext = False
        i_files_in_dir = 0
        while not flag_exist_ext and i_files_in_dir < len(files):
            if os.path.splitext(files[i_files_in_dir])[1] in extension_list:
                flag_exist_ext = True
            i_files_in_dir += 1

        # если файлы из extension_list есть в папке, то ищутся файлы малой длины и удаляются
        # потому что они создаются в момент блокировки архиватором открытой базы, но "пустые"
        if flag_exist_ext:
            print()
            print(folders)

            # поиск фалов малой длины и удаление их
            for file in files:
                if os.path.splitext(file)[1] in extension_list:
                    count_arc_files += 1
                    print(' '*3, file, '.'*(max_space - len(file)),
                          '.. размер = ', human_read_format(os.stat(os.path.join(folders, file)).st_size),
                          ' ... в байтах = ', os.stat(os.path.join(folders, file)).st_size,
                          ' ... дата = ', os.stat(os.path.join(folders, file)).st_mtime,
                          ' ... дата человеческая = ', human_read_date(os.stat(os.path.join(folders, file)).st_mtime),
                          end=' ', sep=''
                          )

                    # если размер файла меньше минимального, то удалить эти файлы
                    if os.stat(file).st_size <= min_size:
                        print(' '*4, '!!! файл малой длины - удаляю !!!', end=' ', sep='')
                        try:
                            if flag_del:
                                os.remove(file)
                                count_del_files += 1
                            print(' ______________ удалён')
                        except PermissionError as errorPE:
                            print(' '*4 + '_'*50 +
                                  f'Ошибка: нет доступа для удаления файла {errorPE.filename} - {errorPE.strerror}'
                                  )
                        except FileNotFoundError as errorFNFE:
                            print(' '*4+'_'*50 + f'Ошибка: файл не найден {errorFNFE.filename} - {errorFNFE.strerror}')

                    elif os.stat(file).st_size > min_size:
                        print(' '*4, '--- файл больше минимума')
                        list_big_files.append([os.stat(os.path.join(folders, file)).st_mtime,
                                               os.path.join(folders, file)
                                               ])
                    else:
                        print(' '*4, '--- надо подумать')

            # если осталось больше, чем quantity_files_in_dir, то продолжаю их обрабатывать
            if len(list_big_files) > quantity_files_in_dir:
                list_sort_big_files = sorted(list_big_files, key=lambda size_big_file: size_big_file[0], reverse=True)

                for file_data in list_sort_big_files:
                    if list_sort_big_files.index(file_data) >= quantity_files_in_dir:
                        print(f'   удаляю файл {file_data[1]} с датой {human_read_date(file_data[0])}', end='')

                        try:
                            if flag_del:
                                os.remove(file_data[1])
                                count_del_big_files += 1
                            print(' ______________ удалён')
                        except PermissionError as errorPE:
                            print(' '*4 + '_'*50 +
                                  f'Ошибка: нет доступа для удаления файла {errorPE.filename} - {errorPE.strerror}'
                                  )
                        except FileNotFoundError as errorFNFE:
                            print(' '*4+'_'*50 + f'Ошибка: файл не найден {errorFNFE.filename} - {errorFNFE.strerror}')

                    else:
                        print(f'   оставляю файл {file_data[1]} с датой {human_read_date(file_data[0])}')


# новая модная фича как запускать прогу
if __name__ == '__main__':
    kill_proc_winrar()  # удаляю зависшие процессы winrar

    del_arc_files(root_dir_with_files)  # ищу и удаляю "мелкие файлы"

    send_email_stattistics()

    print()
    print(f'закрыты все процессы winrar, свободно места на диске с архивами = {free_space_disk(root_dir_with_files)} ... и статистика на почту отправлена')
