#
# audio - Содержит скрипты отвечающие за звук.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


# Импортируем скрипты:
from . import al
from . import environment
from . import listener
from . import music
from . import sound


# Импортируем основной функционал из скриптов:
from .environment import SoundEnvironment
from .listener    import Listener
from .music       import Music
from .sound       import Sound
