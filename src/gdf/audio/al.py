#
# al.py - Объединяет определённые импорты OpenAL.
#


# Импортируем:
import openal as al
from openal import alc


# Флаг о том, что openal был закрыт:
_opengl_quited_ = False


# Закрыть OpenAL:
def al_quit() -> None:
    global _opengl_quited_
    if _opengl_quited_: return
    _opengl_quited_ = True
    al.oalQuit()


# Если наша программа вылетит из за ошибки, то перед её завершением, выполним функцию ниже в любом случае:
import atexit ; atexit.register(al_quit)
