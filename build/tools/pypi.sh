#!/bin/bash

# Вывод сообщения:
printf "\033c"
echo "INSTALLING PYPI LIBRARIES:"
echo

# Установка зависимостей из pypi.txt:
pip3 install -r ./build/pypi.txt
