#
# net - Содержит скрипты отвечающие за сеть.
#


# Импортируем:
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import json
import socket


# Константы:
TCP_PCSC_VERSION = "v1.0"  # Версия TCP Протокола Подключения Сервер-Клиент.


# Ниже 19 классов-исключений:


# Сетевое исключение:
class NetException(Exception): pass


# Сетевое исключение неправильного ключа-пароля от клиента:
class NetClientKeyWrong(NetException): id_error = 0x1F


# Сетевое исключение превышения ожидания ключа от клиента:
class NetClientKeyTimeout(NetException): id_error = 0x2F


# Сетевое исключение отказа от подключения из за переполнения сервера:
class NetServerOverflow(NetException): id_error = 0x3F


# Сетевое исключение ошибки подключения к сокету, связанная с адресом (socket.gaierror):
class NetAddressRelatedError(NetException): pass


# Сетевое исключение превышено время ожидания подключения (socket.timeout):
class NetConnectingTimedOut(NetException): pass


# Сетевое исключение подключение отклонено (ConnectionRefusedError):
class NetConnectingRefused(NetException): pass


# Сетевое исключение подключение прервано (ConnectionAbortedError):
class NetConnectingAborted(NetException): pass


# Сетевое исключение подключение сброшено (ConnectionResetError):
class NetConnectingResetError(NetException): pass


# Сетевое исключение недействительного адреса (OSError Errno 10049):
class NetAddressInvalid(NetException): pass


# Сетевое исключение недоступной сети (OSError Errno ENETUNREACH):
class NetUnavailable(NetException): pass


# Сетевое исключение сетевой путь к хосту недоступен (OSError Errno EHOSTUNREACH):
class NetHostUnreachable(NetException): pass


# Сетевое исключение от системы:
class NetOSError(NetException): pass


# Сетевое исключение превышено время ожидания соединения (socket.timeout):
class NetConnectionTimeout(NetException): pass


# Сетевое исключение соединение прервано (ConnectionAbortedError):
class NetConnectionAborted(NetException): pass


# Сетевое исключение соединение сброшено (ConnectionResetError):
class NetConnectionResetError(NetException): pass


# Сетевое исключение разорванного сокета:
class NetBrokenPipeError(NetException): pass


# Сетевое исключение потери соединения:
class NetConnectionLost(NetException): pass


# Сетевое исключение тайм-аута:
class NetTimeout(NetException): pass


# Класс сокета:
class NetSocket:
    def __init__(self, socket: socket.socket) -> None:
        self.socket = socket
        self._online_flag_ = False

    # Отправить данные:
    def send_data(self, data: str, encoding: str = "utf-8") -> "NetSocket":
        try: self.socket.sendall(str(data).encode(encoding))
        except (TimeoutError, socket.timeout):
            raise NetTimeout("Send data timed-out.")
        except OSError: return self
        finally: return self

    # Получить данные:
    def recv_data(self, buffer_size: int = 1024, decoding: str = "utf-8") -> str | None:
        try:
            data = self.socket.recv(buffer_size).decode(decoding)
            return data if data != "" else None
        except (TimeoutError, socket.timeout):
            raise NetTimeout("Receive data timed-out.")
        except OSError: return None

    # Отправить пакет данных:
    def send_json(self, data: dict, encoding: str = "utf-8") -> "NetSocket":
        self.send_data(json.dumps(data), encoding)
        return self

    # Получить пакет данных:
    def recv_json(self, buffer_size: int = 1024, decoding: str = "utf-8") -> dict | None:
        data = self.recv_data(buffer_size, decoding)
        return json.loads(data) if data is not None else None

    # Установить таймаут:
    def set_time_out(self, timeout: float) -> "NetSocket":
        self.socket.settimeout(float(timeout))
        return self

    # Установить блокирование потока:
    def set_blocking(self, blocking: bool) -> "NetSocket":
        self.socket.setblocking(blocking)
        return self 

    # Создать сервер:
    def bind(self, host: str, port: int) -> "NetSocket":
        self.socket.bind((str(host).lower(), min(max(int(port), 0), 65535)))
        self._online_flag_ = True
        return self

    # Подключиться к серверу:
    def connect(self, host: str, port: int) -> "NetSocket":
        self.socket.connect((str(host).lower(), min(max(int(port), 0), 65535)))
        self._online_flag_ = True
        return self

    # Принять подключение:
    def accept(self) -> tuple:
        return self.socket.accept()

    # Максимальная очередь на присоединение:
    def listen(self, listen: int) -> "NetSocket":
        self.socket.listen(int(listen))
        return self

    # Узнать, находится ли сокет в сети, или он закрыт:
    def online(self) -> bool:
        return bool(self._online_flag_)

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
        self._online_flag_ = False
        self.socket.close()


# Импортируем скрипты:
from . import tcp


# Импортируем основной функционал из скриптов:
from .tcp  import NetServerTCP, NetClientTCP
