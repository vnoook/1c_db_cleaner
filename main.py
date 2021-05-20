# TODO
# программа, которая:
# 0) закрывает процессы winrar, который делает архивы 1с, в памяти
# 1) следит, чтобы в папке не было больше quantity_files_in_dir файлов заархивированной базы 1с
# 2) проверяет наличие свободного места
# 3) пишет письмо после каждого запуска - статистика действий и свободное место на диске
# План:
# ...
# 5) отправить письмо на ящик с инфой
#     а) логи после удаления
#     б) сколько места на диске
# INSTALL
# pip install psutil

import os
import datetime
import shutil
import psutil
import math
import smtplib
import email.message
import email.utils
import msc  # msc_mail_server, msc_login_user, msc_login_pass,msc_from_address, msc_to_address, msc_msg_subject

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

# список формирования данных для письма
info_message_events = []


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
def send_email_statistics():
    info_message_events.append('***')
    info_message_events.append(f'закрыты все процессы winrar\r\n')
    info_message_events.append(f'свободно места на диске с архивами = {free_space_disk(root_dir_with_files)}\r\n')
    info_message_events.append('eMail was sended by Python 3')

    msg_post = '\r\n'.join(info_message_events)

    # msc.msc_msg = '\r\n'.join(( ))
    #     f'',
    #     f'{msg_post}'

    # msg.as_string()
    # msg.get_body()
    # msg.get_content()
    # msg.preamble()
    # msg.policy

    msg = email.message.EmailMessage()

    # msg['MIME-Version'] = '1.0'
    # msg['Content-Type'] = 'text/plain; charset=utf-8'  # 'text/html; charset=utf-8'

    # msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Date'] = 'Thu, 20 May 2021 08:10:52 +0700'

    # msg['Sender'] = 'Sender111'
    # msg['Reply-To'] = 'Reply-To111'
    # msg['Received'] = 'Received111'
    # msg['Comments'] = 'Comments111'
    # msg['Keywords'] = 'Keywords111'

    msg['Subject'] = msc.msc_msg_subject
    msg['From'] = msc.msc_from_address
    msg['To'] = msc.msc_to_address

    msg['Body'] = 'msg_post msg_post msg_post msg_post msg_post msg_post ' \
                  'msg_post ' \
                  'msg_post ' \
                  'msg_post ' \
                  'msg_post msg_post msg_post msg_post msg_post msg_post ' \
                  'msg_post msg_post msg_post ' \
                  'msg_post msg_post ' \
                  'msg_post ' \
                  'msg_post msg_post ' \
                  'msg_post msg_post msg_post '
    print()
    print(msg_post)
    print(type(msg_post))
    print(dir(msg_post))
    print()
    exit()

    smtp_link = smtplib.SMTP_SSL(msc.msc_mail_server)
    smtp_link.login(msc.msc_login_user, msc.msc_login_pass)
    smtp_link.sendmail(msc.msc_from_address, msc.msc_to_address, msc.msc_msg)
    smtp_link.quit()
    print()
    print('eMail was sended')


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
            info_message_events.append('***')
            info_message_events.append(folders)

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


# новая модная фича как запускать прогу
if __name__ == '__main__':
    kill_proc_winrar()  # удаляю зависшие процессы winrar

    del_arc_files(root_dir_with_files)  # ищу и удаляю "мелкие файлы"

    # print('*'*150)
    # print(*info_message_events, sep='\n')
    # print('*' * 150)
    send_email_statistics()  # отправляется статистика работы

    print()
    print(f'закрыты все процессы winrar, свободно места на диске с архивами = {free_space_disk(root_dir_with_files)}'
          f' ... и статистика на почту отправлена')
