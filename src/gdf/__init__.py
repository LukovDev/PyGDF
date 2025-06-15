#
# gdf - Game Development Framework. Пакет () для разработки игр на Python.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import sys
import platform
from importlib.metadata import version, PackageNotFoundError


# Если ваша версия питона ниже 3.11.0:
if platform.python_version() < "3.11.0":
    sys.exit(
        f"\nGDF-Fatal-Error:\n"
        f"    Sorry, but your python version ({platform.python_version()}) is lower than 3.11.0\n"
        f"    Please update your python to be at least 3.11.0"
    )


# Если версия Numpy выше 1.26.4:
try:
    if version("numpy") > "1.26.4":
        sys.exit(
            f"\nGDF-Fatal-Error:\n"
            f"    Sorry, but your numpy version ({version('numpy')}) is upper than 1.26.4\n"
            f"    Please install numpy==1.26.4"
        )
except PackageNotFoundError:
    sys.exit(
        f"\nGDF-Fatal-Error:\n"
        f"    Numpy is not installed. Please install numpy==1.26.4"
    )


# Получить версию ядра:
def get_version() -> str: return "v1.3-indev"


# Получить полное название системы:
def get_platform() -> str: return platform.platform()


# Получить версию питона:
def get_python() -> str: return platform.python_version()


# Класс который определяет систему на которой запущено ядро:
class CurrentPlatform:
    windows: bool = sys.platform in ["win32"]
    macos:   bool = sys.platform in ["darwin"]
    linux:   bool = sys.platform in ["linux", "linux2"]

    @classmethod
    def name(cls) -> str:
        if cls.windows: return "Windows"
        if cls.macos:   return "MacOS"
        if cls.linux:   return "Linux"
        return "Unknown"


# Модули и скрипты:
from . import audio        # Модуль звука.
from . import graphics     # Модуль графики.
from . import net          # Модуль сети.
from . import physics      # Модуль физики.
from . import controllers  # Контроллеры камеры.
from . import files        # Скрипт отвечающий за файлы.
from . import input        # Скрипт отвечающий за ввод данных.
from . import math         # Скрипт отвечающий за математику.
from . import utils        # Скрипт отвечающий за полезные функции.
