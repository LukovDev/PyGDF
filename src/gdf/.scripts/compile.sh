#!/bin/bash

# Вывод сообщения:
printf "\033c"
echo "COMPILING CYTHON FILES:"
echo

# Компиляция cython кода:
python3 -I compile.py build_ext --inplace
