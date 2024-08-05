#
# physics - Содержит скрипты отвечающие за физику.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


# Импортируем скрипты:
from . import phys2d


# Импортируем основной функционал из скриптов:
from .phys2d import Physics2D, PhysicsError
