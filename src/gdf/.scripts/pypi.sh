#!/bin/bash

# Вывод сообщения:
# printf "\033c"
echo "INSTALLING GDF-CORE PYPI LIBRARIES:"
echo

# Установка зависимостей из pypi.txt:
pip3 install -r ../pypi.txt
