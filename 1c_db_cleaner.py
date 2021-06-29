# TODO
# 1) целостность архивной базы — чтобы в архиве был файл 1Cv8.1CD
# 2) разархивируемость архивных файлов — тестирование на распаковку, чтобы не было битых архивов

# скрипт:
# 1) закрывает процессы winrar в памяти (winrar предварительно делает архивы 1с и раскладывают их по папкам)
# 2) сравнивает в папке файлы по содержимому и удаляет одинаковые оставляя новые по дате
# 3) следит чтобы в папке не было больше quantity_files_in_dir файлов архивных баз 1с и удаляет старые по дате
# 4) пишет письмо после каждого исполнения — статистика действий и свободное место на диске
# ...
# в "соседнем" файле msc.py должны храниться следующие переменные с настоящими значениями
# msc_mail_server = 'smtp.xxx.ru'
# msc_from_address = 'server_mail@xxx.ru'
# msc_login_user = 'server_mail'
# msc_login_pass = 'server_pass'
# msc_to_address = 'admin_mail@yyy.ru'
# msc_msg_subject = 'subject mail and statistic'
# msc_msg = ''
# msc_root_dir_with_files = r'real path for dir'
# msc_quantity_files_in_dir = X
# msc_flag_del = True or False
# msc_flag_mail = True or False
# msc_flag_compare = True or False
# msc_flag_kill_proc = True or False

# ...
# INSTALL
# pip install psutil
# pip install rarfile
# ...

import os
import datetime
import shutil
import psutil
import math
import smtplib
import email
import email.utils
import filecmp
import msc
import rarfile


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
    if msc.msc_flag_kill_proc:
        process_winrar = ['winrar.exe', 'winzip.exe', '7z.exe']
        for process in psutil.process_iter():
            if process.name().lower() in process_winrar:
                process.kill()


# отправка на почту статистики запуска
def send_email_statistics():
    # вставляю техническую инфу для информативности письма вверх
    info_message_events.insert(0, '***')
    info_message_events.insert(1, f'закрыты все процессы winrar, свободно места на диске с архивами = '
                                  f'{free_space_disk(msc.msc_root_dir_with_files)}')

    # список соединённый в текст для формирования тела письма
    msg_body = '\r\n'.join(info_message_events)

    # создание объекта "сообщение"
    msg = email.message.EmailMessage()

    # создание заголовков в письме
    msg.set_type('text/plain; charset=utf-8')
    msg['Date'] = email.utils.formatdate(localtime=True)
    msg['Subject'] = msc.msc_msg_subject
    msg['From'] = msc.msc_from_address
    msg['To'] = msc.msc_to_address
    msg.set_payload(msg_body.encode())

    # отправка письма
    if msc.msc_flag_mail:
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


# функция для определения и удаления "мелких" и одинаковых файлов в папке
def del_arc_files(folder_value):
    for folders, dirs, files in os.walk(folder_value):
        # смена текущей папки для поиска файла
        os.chdir(folders)

        # поиск самого длинного имени в папке для ровного отображения в консоли
        max_space = count_max_name_files(files)

        # список для файлов больше минимального размера
        list_big_files = []
        # список индексов для удаления после сравнения
        list_for_index_del = []

        # нужно ли выводить название папки в консоль или нет, если в папке нет файлов с расширением из extension_list
        # флаг существования файлов с расширением из extension_list
        flag_exist_ext = False
        # количество файлов в папке с расширением из extension_list
        i_files_in_dir = 0
        while not flag_exist_ext and i_files_in_dir < len(files):
            if os.path.splitext(files[i_files_in_dir])[1] in extension_list:
                flag_exist_ext = True
            i_files_in_dir += 1

        # если файлы из extension_list есть в папке, то ищутся файлы малой длины и удаляются
        # потому что они создаются архиватором в момент блокировки открытой базы, то есть будут "пустые" или "неполные"
        # также удаляются одинаковые по содержанию файлы
        if flag_exist_ext:
            print()
            print(folders)

            # МАЛАЯ ДЛИНА
            # поиск файлов малой длины и их удаление
            for file in files:
                if os.path.splitext(file)[1] in extension_list:
                    print(' '*3, file, '.'*(max_space - len(file)),
                          ' ... размер в байтах ', os.stat(os.path.join(folders, file)).st_size,
                          ' .. ', human_read_format(os.stat(os.path.join(folders, file)).st_size),
                          ' ... дата ', os.stat(os.path.join(folders, file)).st_mtime,
                          ' .. ', human_read_date(os.stat(os.path.join(folders, file)).st_mtime),
                          end=' ', sep=''
                          )

                    # если размер файла меньше минимального, то удалить эти файлы
                    if os.stat(file).st_size <= min_size:
                        print(' '*4, '!!! файл малой длины - удОли !!!', end=' ', sep='')
                        try:
                            if msc.msc_flag_del:
                                os.remove(file)
                            print(' ______________ удалён')
                        except PermissionError as errorPE:
                            print(' '*4 + '_'*50 +
                                  f'Ошибка: нет доступа для удаления файла {errorPE.filename} - {errorPE.strerror}'
                                  )
                        except FileNotFoundError as errorFNFE:
                            print(' '*4+'_'*50 + f'Ошибка: файл не найден {errorFNFE.filename} - {errorFNFE.strerror}')

                    elif os.stat(file).st_size > min_size:
                        print(' - файл больше минимума')
                        # формирование списка файлов больше "минимума" для дальнейшего сравнения их
                        list_big_files.append([os.stat(os.path.join(folders, file)).st_mtime,
                                               os.path.join(folders, file),
                                               os.stat(os.path.join(folders, file)).st_size
                                               ])

            # СРАВНЕНИЕ
            # поиск файлов одинаковых по содержанию и их удаление
            # если в папке осталось больше одного файла, то можно начать сравнивать
            if msc.msc_flag_compare:
                if len(list_big_files) > 1:
                    # сортировка списка больших файлов по размеру, потом по дате и потом по имени
                    list_big_files = sorted(list_big_files, key=lambda nud: (nud[2], nud[0], nud[1]))

                    # переменные для сохранения предыдущего файла
                    f_date = 0
                    f_name = 0
                    f_size = 0

                    # берём каждый файл и сравниваем с предыдущим
                    for file in list_big_files:
                        # если первый индекс, то просто запоминаем
                        if list_big_files.index(file) == 0:
                            f_file = file
                            f_date = file[0]
                            f_name = file[1]
                            f_size = file[2]
                        else:
                            # сравнение начинается со второго файла
                            if f_size == file[2]:
                                # само сравнение файла на одинаковость содержимого
                                flag_compare = filecmp.cmp(f_name, file[1], shallow=True)

                                # если файлы одинаковые, то удалить предыдущий
                                if flag_compare:
                                    # запоминаю индекс для последующего удаления из списка list_big_files
                                    list_for_index_del.append(list_big_files.index(f_file))

                                    if msc.msc_flag_del:
                                        try:
                                            os.remove(f_name)
                                        except PermissionError as errorPE:
                                            print(' ' * 4 + '_' * 50 +
                                                  f'Ошибка: нет доступа для удаления файла {errorPE.filename} - '
                                                  f'{errorPE.strerror}'
                                                  )
                                        except FileNotFoundError as errorFNFE:
                                            print(
                                                ' ' * 4 + '_' * 50 + f'Ошибка: файл не найден {errorFNFE.filename} - '
                                                                     f'{errorFNFE.strerror}')
                            # переменные сохраняющие текущий файл как предыдущий
                            f_file = file
                            f_date = file[0]
                            f_name = file[1]
                            f_size = file[2]
                # зачистка списка
                # чистка списка list_big_files от записей о файлах которые физически удалены
                for f_ind in list_for_index_del[::-1]:
                    del list_big_files[f_ind]



            # ЦЕЛОСТНОСТЬ файлов
            print('\n', '_'*50)

            list_for_index_del = []

            for big_file in list_big_files:
                print(big_file[1])

                flag_1cd_ext = False
                rf = rarfile.RarFile(big_file[1])

                for f in rf.infolist():
                    if f.is_file():
                        if '1cv8.1cd'.lower() == str(os.path.basename(f.filename)).lower():
                            flag_1cd_ext = True

                if flag_1cd_ext:
                    # запоминаю индекс для последующего удаления из списка list_big_files
                    list_for_index_del.append(list_big_files.index(big_file))

                    try:
                        os.remove(os.path.basename(f.filename))
                    except PermissionError as errorPE:
                        print(' ' * 4 + '_' * 50 +
                              f'Ошибка: нет доступа для удаления файла {errorPE.filename} - '
                              f'{errorPE.strerror}'
                              )
                    except FileNotFoundError as errorFNFE:
                        print(
                            ' ' * 4 + '_' * 50 + f'Ошибка: файл не найден {errorFNFE.filename} - '
                                                 f'{errorFNFE.strerror}')

            # зачистка списка
            # чистка списка list_big_files от записей о файлах которые физически удалены
            for f_ind in list_for_index_del[::-1]:
                del list_big_files[f_ind]

            print('_'*50)



            # ОСТАВИТЬ quantity_files_in_dir ФАЙЛОВ
            # если осталось больше, чем quantity_files_in_dir, то продолжаю их обрабатывать
            # этот кусок кода должен быть последним, потому что этот код должен выбирать только из "здоровых" файлов
            if len(list_big_files) > msc.msc_quantity_files_in_dir:
                # добавление информации в письмо
                info_message_events.append('***')
                info_message_events.append(folders)

                # список больших файлов сортируется по дате
                list_big_files = sorted(list_big_files, key=lambda size_big_file: size_big_file[0], reverse=True)

                # пройдясь по всем файлам проверяется количество файлов оставшихся
                for file_data in list_big_files:
                    if list_big_files.index(file_data) >= msc.msc_quantity_files_in_dir:
                        print(f'   удаляю файл {file_data[1]} с датой {human_read_date(file_data[0])}', end='')
                        info_message_events.append(f'      удаляю файл {os.path.basename(file_data[1])}'
                                                   f' с датой {human_read_date(file_data[0])}'
                                                   f' и размером {human_read_format(os.stat(file_data[1]).st_size)}')
                        try:
                            if msc.msc_flag_del:
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
                        info_message_events.append(f'   оставляю файл {os.path.basename(file_data[1])}'
                                                   f' с датой {human_read_date(file_data[0])}'
                                                   f' и размером {human_read_format(os.stat(file_data[1]).st_size)}')


if __name__ == '__main__':

    kill_proc_winrar()  # удаляю зависшие процессы
    del_arc_files(msc.msc_root_dir_with_files)  # ищу и удаляю файлы
    send_email_statistics()  # отправляется статистика работы

    print()
    print(f'закрыты все процессы winrar,'
          f' свободно места на диске с архивами = {free_space_disk(msc.msc_root_dir_with_files)}'
          f' статистика на почту {msc.msc_to_address} отправлена')
