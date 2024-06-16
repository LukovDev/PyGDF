#
# net - Содержит скрипты отвечающие за сеть.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


# Импортируем скрипты:
from . import client
from . import server
from . import tcpip


# Импортируем основной функционал из скриптов:
from .client import NetClient
from .server import NetServer
from .tcpip  import NetTCPIP
