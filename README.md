# 1C db cleaner
 
Скрипт, который из планировщика следит за папками в которых лежат файловые заархивированные базы 1с:
 
 
* закрывает процессы winrar в памяти (winrar предварительно делает архивы 1с и складывает их по папкам)
 
 
* следит, чтобы в папке не было больше {quantity_files_in_dir} файлов заархивированной базы 1с и удаляет старые по дате
 
 
* пишет письмо после каждого исполнения - статистика действий и свободное место на диске
