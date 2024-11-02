#
# compile.py - В основном нужен для компиляции Cython файлов и для прочих настроек ядра.
#
# Запуск этого скрипта: python setup.py build_ext --inplace
#


# Импортируем:
import os
import glob
import numpy
import shutil
from setuptools import setup, Extension
from Cython.Build import cythonize


# Функция для поиска всех файлов определённого формата:
def find_files(format: str) -> list:
    return glob.glob(f"**/*.{format}", recursive=True)


# Удалить мусор:
def clear() -> None:
    for file in find_files("c"):
        try: os.remove(file)
        except Exception as error:
            print(f"Deleting \"{file}\" failed.")

    build_directory = "build"
    if os.path.exists(build_directory):
        shutil.rmtree(build_directory)


# Установка всех нужных библиотек:
os.system("pip3 install -r pypi.txt")


# Найти файлы .cyt и переименовать их в .pyx:
cyt_files = find_files("cyt")
for file in cyt_files:
    pyx_file = file[:-4] + ".pyx"
    os.rename(file, pyx_file)  # Переименовать .cyt в .pyx


# Устанавливаем ядро:
try:
    setup(
        ext_modules=cythonize([
            Extension(
                name=os.path.splitext(os.path.relpath(file))[0].replace(os.path.sep, "."),
                sources=[file],
                include_dirs=[numpy.get_include()]
            ) for file in find_files("pyx")
        ])
    )
except Exception as error: pass


# Переименовать файлы обратно из .pyx в .cyt:
for file in find_files("pyx"):
    cyt_file = file[:-4] + ".cyt"
    os.rename(file, cyt_file)


# Удаляем мусор:
clear()
