#!/usr/bin/env python
from utils import ALGORITHMS, make_dirs

# Settings
CHOSEN_ALGORITHM = 1  # Выберите алгоритм один из четырех
CSV_FILE = 'pp-complete.csv'  # Файл с контрактами
RESULT_FILE = 'result.txt'  # Файл с результатами


def main():
    make_dirs()
    ALGORITHMS.get(CHOSEN_ALGORITHM)(CSV_FILE, RESULT_FILE)


if __name__ == '__main__':
    main()
