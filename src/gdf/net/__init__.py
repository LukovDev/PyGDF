#
# net - Содержит скрипты отвечающие за сеть.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"


""" Коды ошибок:
    000 - Unknown error                          - Неизвестная сетевая ошибка.

    001 - Invalid server address (IP or Port)    - Адрес сервера не правильный (или ip или порт сервера).

    002 - Connection Timeout                     - Время ожидания соединения с сервером или клиентом истекло.

    003 - The server actively refuses to connect - Сервер отказывается соединять нас (точная причина может быть другой).

    004 - The specified hostname does not exist  - Имя хоста не существует или не может быть разрешён.

    005 - Server Error                           - Неизвестная ошибка в работе сервера.

    006 - The selected Port is already occupied  - Выбранный порт уже занят.

    007 - This address is invalid                - Адрес на котором создаётся сервер, неправильный или недопустим.

    008 - Error when handling client             - Неизвестная ошибка при работе с клиентом на стороне сервера.

    009 - Connection Lost                        - Соединение с сервером или клиентом прервано.
"""


# Сетевое исключение:
class NetException(Exception): pass


# Сетевое исключение тайм-аута:
class NetTimeOut(NetException): pass


# Сетевое исключение потери соединения:
class NetConnectLost(NetException): pass


# Сетевое исключение отказа узла от соединения:
class NetConnectionRefused(NetException): pass


# Импортируем скрипты:
from . import tcp


# Импортируем основной функционал из скриптов:
from .tcp  import NetServerTCP, NetClientTCP, NetSocket
