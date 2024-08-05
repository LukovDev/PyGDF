#
# al.py - Объединяет определённые импорты OpenAL.
#


# Импортируем:
import openal as al
from openal import alc

# Если наша программа вылетит из за ошибки, то перед её завершением, выполним функцию ниже в любом случае:
import atexit
atexit.register(al.oalQuit)
