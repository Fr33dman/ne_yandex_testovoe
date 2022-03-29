#!/usr/bin/env python
import time

from utils import SimpleBot


def main():
    bot = SimpleBot()
    bot.work(1)
    time.sleep(300)


if __name__ == '__main__':
    main()
