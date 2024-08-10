#
# setup.py - В основном нужен для компиляции Cython файлов и для прочих настроек ядра.
#
# Запуск этого скрипта: python setup.py build_ext --inplace
#


# Импортируем:
import os
import glob
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


# Устанавливаем ядро:
setup(
    ext_modules = cythonize([
        Extension(
            name=os.path.splitext(os.path.relpath(file))[0].replace(os.path.sep, "."),
            sources=[file]
        ) for file in find_files("pyx")
    ])
)


# Удаляем мусор:
clear()
