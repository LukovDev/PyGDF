#
# setup.py - Нужен для упаковки ядра.
#
# Для упаковки в .whl: python setup.py bdist_wheel
#


# Импортируем:
import os
import shutil
from setuptools import setup, find_packages


def load_requirements(file):
    with open(file) as f:
        return [line.strip() for line in f if line and not line.startswith("#")]


# Упаковываем ядро:
setup(
    name                 = "gdf",
    version              = "1.0",
    description          = "Python Game Development Framework (PyGDF or GDF-Core)",
    package_dir          = {"": "../src/"},
    packages             = find_packages(where="../src/"),
    author               = "LukovDev",
    author_email         = "lakuworx@gmail.com",
    url                  = "https://pygdf.github.io/",
    python_requires      = ">=3.11",
    zip_safe             = False,
    keywords             = "game development framework",
    license              = "MIT",
    include_package_data = True,
    install_requires     = load_requirements("../src/gdf/pypi.txt"),
)


# Очищаем мусор:
build_dir    = "build"
egg_info_dir = "../src/gdf.egg-info"
dist_dir     = "dist"


# Функция для удаления папки, если она существует:
def remove_dir(dir_path):
    if os.path.exists(dir_path): shutil.rmtree(dir_path)


# Удаляем папки build и gdf.egg-info:
remove_dir(build_dir)
remove_dir(egg_info_dir)


# Перемещаем содержимое из dist в текущую папку:
if os.path.exists(dist_dir):
    for item in os.listdir(dist_dir):
        s = os.path.join(dist_dir, item)
        d = os.path.join(os.getcwd(), item)
        if os.path.isdir(s):
            shutil.move(s, d)
        else: shutil.move(s, d)

    # Удаляем папку dist:
    shutil.rmtree(dist_dir)


# Переименовываем полученный файл:

# Исходное имя файла:
old_wheel_name = "gdf-1.0-py3-none-any.whl"

# Новая часть имени, на которую нужно заменить:
new_suffix = "cp311-cp311-win_amd64.whl"

if "py3" in old_wheel_name:
    new_wheel_name = old_wheel_name[:old_wheel_name.index("py3")] + new_suffix
    if os.path.exists(new_wheel_name): os.remove(new_wheel_name)
    os.rename(old_wheel_name, new_wheel_name)
