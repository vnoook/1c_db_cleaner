# 1C_DB_cleaner
 
Скрипт из планировщика следит за папками, в которых лежат файловые заархивированные базы 1с:
 
 
* закрывает процессы winrar в памяти (winrar предварительно делает архивы 1с и складывает их по папкам)
 
 
* следит, чтобы в папке не было больше msc_quantity_files_in_dir файлов заархивированной базы 1с, я для этого:
 
     сравнивает файлы по содержимому и удаляет старые по дате
 
     удаляет оставшиеся "лишние" файлы по дате
 
 
* пишет письмо после каждого исполнения со статистикой действий и свободным местом на текущем диске
