# программа:
# 1) закрывает процессы winrar в памяти, winrar делает архивы 1с и складывают по папкам
# 2) следит, чтобы в папке не было больше quantity_files_in_dir файлов заархивированной базы 1с и удаляет лишние
# 3) пишет письмо после каждого исполнения - статистика действий и свободное место на диске
# ...
# INSTALL
# pip install psutil

import os
import datetime
import shutil
import psutil
import math
import smtplib
import email
import email.utils
import msc

# переменная удаления файлов, True удаляет файлы физически
flag_del = False

# папка для поиска папок с архивами
root_dir_with_files = r'd:\tmp'

# количество архивов одного экземляра базы в папке
quantity_files_in_dir = 5

# расширения файлов для поиска в папке
extension_list = ('.rar', '.zip', '.dt', '.7z')

# размер файла в байтах "минимального размера"
min_size = 10485760  # 10 Mb

# список формирования данных для письма
info_message_events = []


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


# удаляет процессы winrar в памяти
def kill_proc_winrar():
    process_winrar = 'winrar.exe'
    for process in psutil.process_iter():
        if process.name().lower() == process_winrar:
            process.kill()


# отправка на почту статистики запуска
def send_email_statistics():
    # вставляю техническую инфу для информативности письма вверх
    info_message_events.insert(0, '***')
    info_message_events.insert(1, f'закрыты все процессы winrar, свободно места на диске с архивами ='
                                  f' {free_space_disk(root_dir_with_files)}')

    # список соединённый в текст для формирования тела письма
    msg_body = '\r\n'.join(info_message_events)

    # создание объекта "сообщение"
    msg = email.message.EmailMessage()

    # создание заголовков в письме
    msg.set_content('some text')  # ???????????????????????????????????????????????????????????????????????????
    msg.set_type('text/plain; charset=utf-8')
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Subject'] = msc.msc_msg_subject
    msg['From'] = msc.msc_from_address
    msg['To'] = msc.msc_to_address
    msg.set_payload(msg_body.encode())

    # отправка письма
    smtp_link = smtplib.SMTP_SSL(msc.msc_mail_server)
    smtp_link.login(msc.msc_login_user, msc.msc_login_pass)
    smtp_link.send_message(msg, msc.msc_from_address, msc.msc_to_address)
    smtp_link.quit()

    print()
    print('eMail sent')


# подсчёт самого длинного названия файла в папке для ровного отображения в консоли
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

        # поиск самого длинного имени в папке для ровного отображения в консоли
        max_space = count_max_name_files(files)

        # количество файлов из extension_list
        count_arc_files = 0

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
        # потому что они создаются архиватором в момент блокировки открытой базы, но "пустые"
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
                info_message_events.append('***')
                info_message_events.append(folders)

                list_sort_big_files = sorted(list_big_files, key=lambda size_big_file: size_big_file[0], reverse=True)

                for file_data in list_sort_big_files:
                    if list_sort_big_files.index(file_data) >= quantity_files_in_dir:
                        print(f'   удаляю файл {file_data[1]} с датой {human_read_date(file_data[0])}', end='')
                        info_message_events.append(f'   удаляю файл {file_data[1]}'
                                                   f' с датой {human_read_date(file_data[0])}')

                        try:
                            if flag_del:
                                os.remove(file_data[1])
                            print(' ______________ удалён')
                        except PermissionError as errorPE:
                            print(' '*4 + '_'*50 +
                                  f'Ошибка: нет доступа для удаления файла {errorPE.filename} - {errorPE.strerror}'
                                  )
                        except FileNotFoundError as errorFNFE:
                            print(' '*4+'_'*50 + f'Ошибка: файл не найден {errorFNFE.filename} - {errorFNFE.strerror}')

                    else:
                        print(f'   оставляю файл {file_data[1]} с датой {human_read_date(file_data[0])}')
                        info_message_events.append(f'   оставляю файл {file_data[1]}'
                                                   f' с датой {human_read_date(file_data[0])}')

if __name__ == '__main__':

    kill_proc_winrar()  # удаляю зависшие процессы winrar
    del_arc_files(root_dir_with_files)  # ищу и удаляю "мелкие файлы"
    send_email_statistics()  # отправляется статистика работы

    print()
    print(f'закрыты все процессы winrar,'
          f' свободно места на диске с архивами = {free_space_disk(root_dir_with_files)}'
          f' статистика на почту {msc.msc_to_address} отправлена')
