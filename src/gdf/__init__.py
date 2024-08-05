#
# gdf - Пакет (встраиваемая библиотека) для разработки игр.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import sys
import platform


# Получить версию библиотеки:
def get_version() -> str: return "v1.0-release"


# Получить полное название системы:
def get_platform() -> str: return platform.platform()


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


# Если ваша версия питона ниже 3.11.0:
if platform.python_version() < "3.11.0":
    sys.exit(
        f"\nGDF-Error:\n"
        f"    Sorry, but your python version ({platform.python_version()}) is lower than 3.11.0\n"
        f"    Please update your python to be at least 3.11.0"
    )
