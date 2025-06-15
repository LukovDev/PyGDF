#
# al.py - Объединяет определённые импорты OpenAL.
#


# Импортируем:
import os
import sys
from .. import CurrentPlatform


# Если ядро запущено на макос, то вручную указываем путь до OpenAL-Soft (по умолчанию этой библиотеки нет на macos):
if CurrentPlatform.macos:
    # Если мы собрали программу, то ищем библиотеку в файлах нашей сборки:
    if hasattr(sys, "_MEIPASS"): path = os.path.join(sys._MEIPASS, "gdf/audio/")
    # Иначе если (по всей видимости) запустили из исходного кода, ищем там где находится этот скрипт:
    else: path = os.path.split(os.path.abspath(__file__))[0]
    # Указываем путь до папки где находится библиотека OpenAL:
    os.environ["DYLD_LIBRARY_PATH"] = path


# Импортируем:
try:
    import openal as al
    from openal import alc
except ImportError as error:
    raise Exception(f"PyOpenAL is not installed.")
except Exception as error:
    raise Exception(f"OpenAL not found on your device.")

from .sound import _all_sounds_


# Флаг о том, что openal был закрыт:
_opengl_quited_ = False


# Закрыть OpenAL:
def al_quit() -> None:
    global _all_sounds_, _opengl_quited_
    for sound in _all_sounds_: sound.destroy()
    _all_sounds_.clear()
    if _opengl_quited_: return
    _opengl_quited_ = True
    al.oalQuit()


# Если наша программа вылетит из за ошибки, то перед её завершением, выполним функцию ниже в любом случае:
import atexit; atexit.register(al_quit)
