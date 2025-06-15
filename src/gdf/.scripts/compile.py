#
# compile.py - В основном нужен для компиляции Cython файлов и для прочих настроек ядра.
#
# Запуск этого скрипта: python -I compile.py build_ext --inplace
# Флаг -I нужен чтобы пайтон запустил скрипт изолировано, чтобы этот скрипт и библиотеки не могли
# импортировать локальные модули и файлы.
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


# Устанавливаем ядро:
try:
    os.chdir("../")
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


# Удаляем мусор:
print("\nDeleting temporary build files... ", end="")
clear()
print("Done!")
