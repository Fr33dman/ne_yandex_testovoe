#!/usr/bin/env sh

# Миграция
alembic upgrade head

# Запуск команды
python main.py
