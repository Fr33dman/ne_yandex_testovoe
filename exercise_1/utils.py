"""
Это первое задание. Изначально из формулировки задания не было понятно, что именно нужно вывести - контракты на дома,
которые продали больше одного раза или адрес с контрактами ниже или просто список адресов. По итогу был выбран последний
вариант, потому что первые не выглядят логичными (ведь мы на то и делаем поиск, чтобы из контрактов вытянуть адреса).
Таким образом я сделал несколько алгоритмов:

1) find_duplicates_easy_way - самый простой и банальный способ, просто в лоб парсим файл и считаем кто сколько раз нам
попался. Он самый простой, но и по идее самый эффективный по времени (но он держит в памяти сразу весь словарь,
что ест много памяти).

2) find_duplicates_external_search - самый криво написанный но по идее самый менее жрущий память алгоритм - обрабатывает файл
чанками и загружает их в файлы на диск в виде jsonов, а дальше склеивает (его можно очень сильно усовершенствовать, но
мне пока что не хватило знаний, чтобы это сделать).

3) find_duplicates_regex - то же что и первый алгоритм, только через регулярку - чем меньше файл, тем быстрее работает.
Если бы файл был до гигабайта - то он был бы самым лучшим среди всех.

4) find_duplicates_split - поэкспериментировал со стандартными фукнциями питона, если файл небольшой то по времени он
работает еще быстрее чем третий алгоритм, но... это колхоз)) никто в здравом уме так делать не будет, поэтому алгоритм
чисто экспериментальный, но на срезе до миллиона строк он себя показывал очень даже шустро (после миллиона он может
просто так выдать 170 секунд, причем непонятно почему, лучший результат что я получил это 140 секунд)

Вот результаты тестов алгоритмов:

===============================
Function: find_duplicates_easy_way
Memory before: 12,140,544
Memory after: 12,992,512
Memory consumed: 851,968
Time: 124.14728617668152
===============================

===============================
Function: find_duplicates_external_search
Memory before: 11,927,552
Memory after: 1,207,910,400
Memory consumed: 1,195,982,848
Time: 295.1373801231384
===============================

===============================
Function: find_duplicates_regex
Memory before: 11,927,552
Memory after: 16,252,928
Memory consumed: 4,325,376
Time: 184.78774785995483
===============================

===============================
Function: find_duplicates_split
Memory before: 11,894,784
Memory after: 12,337,152
Memory consumed: 442,368
Time: 140.17971396446228
===============================

При всех моих попытках оптимизировать второй алгоритм, сильно уменьшить использование памяти мне не удалось (точнее
это привело к троекратному увеличению времени). Я думаю что счетчик памяти немного врет и второй алгоритм в моменте
должен использовать памяти меньше чем другие, но в конце слияния образуется узкое горлышко, которое я не придумал как
убрать, но я думаю что если его еще доработать, то он был бы самым оптимальным, возможно мне не хватило опыта и знаний,
чтобы довести его до ума, а может я не додумался до чего то элементарного и переусложнил код.

По итогу самый нормальный алгоритм - это первый, который был написан за 10 минут, а на остальные ушло 2 дня
"""


import csv
import random
from collections import defaultdict
import os
import re
import json

# -------------------- Track time and memory --------------------

# import time
# import psutil


# Для использования трэка времени требуется библиотека psutil
#
# def elapsed_since(start):
#     return time.time() - start
#
#
# def get_process_memory():
#     process = psutil.Process(os.getpid())
#     return process.memory_info().rss
#
#
# def track(func):
#     def wrapper(*args, **kwargs):
#         mem_before = get_process_memory()
#         start = time.time()
#         result = func(*args, **kwargs)
#         elapsed_time = elapsed_since(start)
#         mem_after = get_process_memory()
#         print("\n\n"
#               "===============================\n"
#               "Function: {}\n"
#               "Memory before: {:,}\n"
#               "Memory after: {:,}\n"
#               "Memory consumed: {:,}\n"
#               "Time: {}\n"
#               "==============================="
#               "\n\n".format(
#             func.__name__,
#             mem_before, mem_after, mem_after - mem_before,
#             elapsed_time))
#         return result, elapsed_time
#     return wrapper

# ---------------------------------------------------------------


def make_dirs():
    """
    Создает необходимые директории
    :return: None
    """
    dirs = ('results', 'buffer_results', 'buffer')
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)


def write_file(addresses: list, result_file: str):
    """
    Запись списка адресов в файл (актуально только для easy, regex и split функций)
    :param addresses: список адресов
    :param result_file: имя файла в который будет записан словарь
    :return: None
    """
    with open(f'results/{result_file}', 'w') as file:
        for address in addresses:
            address = address.replace('  ', ' ')
            address = f'{address}\n'
            file.writelines(address)


class Buffer:
    """
    Класс буффер для сохранения словарей в постоянной памяти
    """

    buffer_files = []  # Список названий файлов в буффере
    result_files = []  # Список названий файлов с уже найденными дублями адресов

    def add(self, data: dict or list, result: bool = False):
        """
        Сохраняет объект в файл
        :param data: Объект, который будет сохранен в формате json
        :param result: Режим записи, если True то запись в результат, если False то в буффер
        :return: None
        """
        data = json.dumps(data)
        directory = 'buffer_results' if result else 'buffer'
        filename = f'{directory}/{"".join([random.choice("abcdefghijklmnopqrstyvwxyz1234567890") for x in range(15)])}.json'
        with open(filename, 'w') as file:
            file.write(data)
        if result:
            self.result_files.append(filename)
        else:
            self.buffer_files.append(filename)

    def merge_dicts(self, dict_1: dict, dict_2: dict):
        """
        Мерджит и разделяет словари
        :param dict_1: Словарь со счетчиками
        :param dict_2: Словарь со счетчиками
        :return: None
        """

        # Убираем коллизии ключей - если в двух словарях встречается один и тот же ключ то объединяем списки
        duplicated_keys = [key for key in dict_1.keys() if key in dict_2]
        for key in duplicated_keys:
            dict_1[key] += dict_2[key]
            dict_2.pop(key)
        # Объединяем словари в один общий из которого получим два:
        # 1) тот, у которого счетчик уже больше 2 - его уже можно отправить в результаты
        # 2) тот, у которого счетчик еще равен 1 - его дальше отправляем
        # в буффер для сравнения с другими чанками словарей
        dict_result = dict(**dict_1, **dict_2)

        # Список с уже найденными счетчиками
        list_duplicates = list(key for key, value in dict_result.items() if value > 1)

        # Словарь без дубликатов, который дальше отправляем в буфер для дальнейшей сортировки с другими чанками
        dict_non_duplicates = dict(filter(lambda x: x[1] == 1, dict_result.items()))

        if dict_non_duplicates:
            self.add(dict_non_duplicates)
        if list_duplicates:
            self.add(list_duplicates, result=True)

    def merge_lists(self, list_1: list, list_2: list):
        """
        Мерджит листы (предварительно убирая дубликаты преобразованием в массив)
        :param list_1: Список адресов
        :param list_2: Список адресов
        :return: None
        """
        list_1.extend(list_2)
        del list_2
        list_1 = list(set(list_1))
        self.add(list_1, result=True)

    def merge_files(self, filename_1: str, filename_2: str, result: bool = False):
        """
        Мерджит промежуточные файлы в один
        :param filename_1: Название файла
        :param filename_2: Название файла
        :param result: Режим мерджа, если True то мердж списков, если False то мердж словарей
        :return: None
        """
        with open(filename_1) as file_1:
            data_1 = json.loads(file_1.read())
        with open(filename_2) as file_2:
            data_2 = json.loads(file_2.read())
        if result:
            self.merge_lists(data_1, data_2)
            del data_1, data_2
            self.result_files.remove(filename_1)
            self.result_files.remove(filename_2)
        else:
            self.merge_dicts(data_1, data_2)
            del data_1, data_2
            self.buffer_files.remove(filename_1)
            self.buffer_files.remove(filename_2)
        os.remove(filename_1)
        os.remove(filename_2)

    def merge(self) -> list:
        """
        Производит мердж и сортировку всех файлов из буффера в конечный файл со списком адресов и возвращает адреса
        :return: Список уже собранных адресов
        """
        while len(self.buffer_files) > 1:
            self.merge_files(self.buffer_files[0], self.buffer_files[1])
        os.remove(self.buffer_files[0])
        while len(self.result_files) > 1:
            self.merge_files(self.result_files[0], self.result_files[1], result=True)
        with open(self.result_files[0]) as result_file:
            result = json.loads(result_file.read())
        os.remove(self.result_files[0])
        return result


def process_chunk(chunk: list) -> defaultdict:
    """
    Собирает словарь где ключ - это строка, а значение - счетчик
    :param chunk: Список строк из csv файла
    :return: Словарь со счетчиками повторений адресов
    """
    addresses = defaultdict(int)
    for i, row in enumerate(chunk):
        address = ' '.join(row[7:14])
        addresses[address] += 1
    return addresses


# @track
def find_duplicates_easy_way(csv_file, result_file):
    addresses = defaultdict(int)
    with open(csv_file) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            address = tuple(row[7:14])
            addresses[address] += 1
    addresses = list(' '.join(key) for key, value in addresses.items() if value > 1)
    write_file(addresses, result_file)


# @track
def find_duplicates_external_search(csv_file, result_file):
    buffer = Buffer()
    chunk_size = 2000000
    chunk = []
    with open(csv_file) as csvfile:
        reader = csv.reader(csvfile)
        for index, line in enumerate(reader):
            if index % chunk_size == 0 and index > 0:
                addresses = process_chunk(chunk)
                del chunk[:]
                buffer.add(addresses)
                del addresses
            chunk.append(line)
        if chunk:
            addresses = process_chunk(chunk)
            del chunk[:]
            buffer.add(addresses)
            del addresses
    addresses = buffer.merge()
    write_file(addresses, result_file)


# @track
def find_duplicates_regex(csv_file, result_file):
    regex = re.compile(r'\"([^\"]*)\",?'*16, flags=re.IGNORECASE | re.MULTILINE)

    addresses = defaultdict(int)
    with open(csv_file) as csvfile:
        for row in csvfile.readlines():
            # row = csvfile.readline()
            match = re.match(regex, row).groups()
            address = tuple(match[7:14])
            addresses[address] += 1
    addresses = list(' '.join(key) for key, value in addresses.items() if value > 1)
    write_file(addresses, result_file)


# @track
def find_duplicates_split(csv_file, result_file):
    addresses = defaultdict(int)
    with open(csv_file) as csvfile:
        for row in csvfile.readlines():
            row = row.replace('"', '').split(',')
            address = tuple(row[7:14])
            addresses[address] += 1
    addresses = list(' '.join(key) for key, value in addresses.items() if value > 1)
    write_file(addresses, result_file)


ALGORITHMS = {
    1: find_duplicates_easy_way,
    2: find_duplicates_external_search,
    3: find_duplicates_regex,
    4: find_duplicates_split,
}


if __name__ == '__main__':
    filename = 'pp-complete.csv'
    find_duplicates_easy_way(filename, 'results/result_file_easy_way.txt')
    find_duplicates_external_search(filename, 'results/result_file_external_search.txt')
    find_duplicates_regex(filename, 'results/result_file_regex.txt')
    find_duplicates_split(filename, 'results/result_file_split.txt')
