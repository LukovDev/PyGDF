#
# net - Содержит скрипты отвечающие за сеть.
#


# Импортируем:
if True:
    import os
    os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

    import json
    import socket


""" Коды ошибок:

    000 - Unknown error                          - Неизвестная сетевая ошибка.

    001 - Invalid server address                 - Адрес сервера не правильный (ip или порт сервера).

    002 - Connection Timeout                     - Время ожидания соединения с сервером или клиентом истекло.

    003 - Connection refused                     - Отказано в соединении. Либо очередь переполнена, либо сервера нет.

    004 - The specified hostname does not exist  - Имя хоста не существует или не может быть разрешён.

    005 - Server Error                           - Неизвестная ошибка в работе сервера.

    006 - The selected Port is already occupied  - Выбранный порт уже занят.

    007 - Address server is being created is invalid - Адрес на котором создаётся сервер, неправильный или недопустим.

    008 - Error when handling client             - Неизвестная ошибка при работе с клиентом на стороне сервера.

    009 - Connection Lost                        - Соединение с сервером или клиентом прервано.

    010 - Server disconnected you due to an incorrect password - Сервер отключил вас, потому что пароль неверен.

    011 - Server disconnected you because it didn't wait for the password - Сервер слишком долго ждал от вас пароль.

    012 - Server disconnected you because server is full       - Сервер отключил вас, потому что он переполнен.

    013 - Connection was not established for an unknown reason - Соединение не было установлено по неизвестной причине.

    014 - Error when handling server             - Неизвестная ошибка при работе с сервером на стороне клиента.

    015 - Server disconnected you because it waited too long for a response - Сервер слишком долго ждал ответа.
"""

""" Все сообщения отправляемые от сервера к клиенту:

    ---------------- При подключении клиента к серверу: ----------------

    "key-success"       - Значит что ключ подошёл, и клиент успешно присоединился к серверу.

    "key-wrong"         - Значит что ключ НЕ подошёл, и клиент был отключён.

    "key-timeout-error" - Значит что сервер слишком долго ждал получения ключа от клиента.

    "server-overflow"   - Значит что сервер переполнен, и присоединиться невозможно.

    ---------------- При обработке клиента сервером: ----------------

    "timeout-disconnect" - Значит что сервер не дождался ответа за timeout времени.

"""


# Сетевое исключение:
class NetException(Exception): pass


# Сетевое исключение тайм-аута:
class NetTimeOut(NetException): pass


# Сетевое исключение тайм-аута соединения:
class NetConnectionTimeOut(NetException): pass


# Сетевое исключение потери соединения:
class NetConnectionLost(NetException): pass


# Сетевое исключение отказа узла от соединения:
class NetConnectionRefused(NetException): pass


# Сетевое исключение отказа от подключения из за переполнения сервера:
class NetServerOverflow(NetException): pass


# Сетевое исключение неправильного ключа-пароля от клиента:
class NetClientKeyWrong(NetException): pass


# Класс сокета:
class NetSocket:
    def __init__(self, socket: socket.socket) -> None:
        self.socket = socket

    # Отправить данные:
    def send_data(self, data: str, encoding: str = "utf-8") -> "NetSocket":
        # Мы добавляем 4 символа в начало сообщения, чтобы клиент не мог отправить пустое сообщение
        # следствием чего, сервер рассчитал бы это как отключение клиента от сервера:
        self.socket.sendall(f"MSG:{data}".encode(encoding))
        return self

    # Получить данные:
    def recv_data(self, buffer_size: int = 1024, decoding: str = "utf-8") -> str:
        # А тут мы просто урезаем первые 4 символа и возвращаем полностью целую чистую оригинальную строку:
        return self.socket.recv(buffer_size).decode(decoding)[4:]

    # Отправить пакет данных:
    def send_json(self, data: dict, encoding: str = "utf-8") -> "NetSocket":
        self.send_data(json.dumps(data), encoding)
        return self

    # Получить пакет данных:
    def recv_json(self, buffer_size: int = 1024, decoding: str = "utf-8") -> dict:
        return json.loads(self.recv_data(buffer_size, decoding))

    # Установить таймаут:
    def set_time_out(self, timeout: float) -> "NetSocket":
        self.socket.settimeout(float(timeout))
        return self

    # Создать сервер:
    def bind(self, host: str, port: int) -> "NetSocket":
        self.socket.bind((str(host).lower(), min(max(int(port), 0), 65535)))
        return self

    # Принять подключение:
    def accept(self) -> tuple:
        return self.socket.accept()

    # Максимальная очередь на присоединение:
    def listen(self, listen: int) -> "NetSocket":
        self.socket.listen(int(listen))
        return self

    # Подключиться к серверу:
    def connect(self, host: str, port: int) -> "NetSocket":
        self.socket.connect((str(host).lower(), min(max(int(port), 0), 65535)))
        return self

    # Получить адрес удалённого узла (сервера или клиента к которому мы подключены):
    def get_peer_name(self) -> tuple:
        return self.socket.getpeername()

    # Получить адрес локального узла (нас):
    def get_sock_name(self) -> tuple:
        return self.socket.getsockname()

    # Получить ip сокета:
    def get_host(self) -> str:
        return self.get_sock_name()[0]

    # Получить порт сокета:
    def get_port(self) -> int:
        return self.get_sock_name()[1]

    # Закрыть сокет:
    def close(self) -> None:
        self.socket.close()


# Импортируем скрипты:
from . import tcp


# Импортируем основной функционал из скриптов:
from .tcp  import NetServerTCP, NetClientTCP
