# block-device-tester
Приложение для тестирования производительности блочного устройства с использованием fio для проведения тестов и gnuplot для визуализации результатов.

## Зависимости

Перед запуском приложения убедитесь, что у вас установлены следующие зависимости:

- [fio](https://fio.readthedocs.io/en/latest/)
- [gnuplot](http://www.gnuplot.info/)
- Python 3

## Установка и запуск
### Локально
1. Склонируйте репозиторий:
```bash
   git clone https://github.com/anemon-a/block-device-tester.git
   cd block-device-tester/src
   chmod +x blktest.py
```
2. Установите зависимости, если они еще не установлены:
```bash
   sudo apt-get update
   sudo apt-get install fio gnuplot
```
Для запуска теста используйте следующую команду:
```bash
./test -name=<имя_теста> -filename=<путь_к_блочному_устройству> -output=<имя_файладля_графика.png>
```
#### Параметры
- -name: Имя теста.
- -filename: Путь к блочному устройству или файлу, который вы хотите протестировать (например, /dev/sda или testfile).
- -output: Имя выходного файла для графика (например, graph.png).
#### Пример
```bash
./test -name=my_test -filename=/dev/sda -output=graph.png
```
## Результаты
После завершения теста вы получите файл graph.png, который содержит график производительности блочного устройства.
