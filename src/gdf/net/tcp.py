#
# tcpip.py - TCP/IP реализация интернет соединения. Реализует класс для передачи данных через TCP/IP протокол.
#


# Импортируем:
if True:
    import time
    import json
    import socket
    from threading import Thread
    from . import *


# Класс сокета:
class NetSocket:
    def __init__(self, socket: socket.socket) -> None:
        self.socket = socket

    # Отправить данные:
    def send_data(self, data: str, encoding: str = "utf-8") -> "NetSocket":
        self.socket.sendall(str(data).encode(encoding))
        return self

    # Получить данные:
    def recv_data(self, buffer_size: int = 1024, decoding: str = "utf-8") -> str:
        return self.socket.recv(buffer_size).decode(decoding)

    # Отправить пакет данных:
    def send_json(self, data: dict, encoding: str = "utf-8") -> "NetSocket":
        self.send_data(json.dumps(data), encoding)
        return self

    # Получить пакет данных:
    def recv_json(self, buffer_size: int = 1024, decoding: str = "utf-8") -> dict:
        return json.loads(self.recv_data(buffer_size, decoding))

    # Установить таймаут:
    def set_time_out(self, timeout: float) -> "NetSocket":
        self.socket.settimeout(timeout)
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
        self.socket.listen(listen)
        return self

    # Подключиться к серверу:
    def connect(self, host: str, port: int) -> "NetSocket":
        self.socket.connect((str(host).lower(), min(max(int(port), 0), 65535)))
        return self

    # Получить ip сокета:
    def get_host(self) -> str:
        return self.socket.getsockname()[0]

    # Получить порт сокета:
    def get_port(self) -> int:
        return self.socket.getsockname()[1]

    # Закрыть сокет:
    def close(self) -> None:
        self.socket.close()


# Класс сервера TCP/IP:
class NetServerTCP:
    def __init__(self, connect_handler: any, client_handler: any, disconnect_handler: any) -> None:
        # Внутренние переменные класса:
        self.connect_handler    = connect_handler     # Вызывается при подключении клиента.
        self.client_handler     = client_handler      # Вызывается каждый 1/TPS раз в отдельном потоке.
        self.disconnect_handler = disconnect_handler  # Вызывается при отключении клиента.

        # Внутренние переменные:
        self.__netvars__ = {
            "clients":       [],     # Список клиентов.
            "connect-limit": int,    # Максимальное количество клиентов.
            "entry-key":     str,    # Ключ входа.
            "tps-limit":     int,    # Частота цикла обработки клиента (сколько раз в сек обработать).
            "timeout":       float,  # Время ожидания ответа между клиентом и сервером.
            "stop-handling": False,  # Остановить обработку подключений и клиентов.
        }

        # Создаём сокет сервера (AF_INET это IPv4 | SOCK_STREAM это TCP):
        self.socket = NetSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    # Обработчик клиентов в отдельном потоке:
    def __client_handler__(self, client: NetSocket, address: tuple) -> None:
        try:
            client.set_time_out(self.__netvars__["timeout"])  # Установка таймаута на ожидание ответа от клиента.

            while True:
                try:
                    # Если мы останавливаем обработку клиентов:
                    if self.__netvars__["stop-handling"]: break

                    # Получаем данные от клиента:
                    data = client.recv_data(1024, "utf-8")

                    # Обрабатываем отключение клиента:
                    if not data: break  # Выходим из бесконечного цикла обработки.

                    # Обрабатываем клиента:
                    self.client_handler(client, address)
                except socket.timeout:
                    break  # Выходим из бесконечного цикла обработки.

                # Делаем некоторую задержку между циклом, чтобы не взорвать провайдера:
                time.sleep(1/self.__netvars__["tps-limit"])
        except ConnectionResetError:
            raise NetConnectLost(f"[009] Connection Lost (with {address[0]}:{address[1]})")
        except Exception as error:
            raise NetException(f"[008] Error when handling client (with {address[0]}:{address[1]}): {error}")
        finally:
            # Удаляем этого клиента из списка:
            self.__netvars__["clients"].remove(client)

            # Обрабатываем отключение клиента:
            self.disconnect_handler(client, address)

            # Закрываем сокет клиента (соединение с клиентом) в любом случае:
            client.close()

    # Обработчик присоединений клиентов к серверу:
    def __connect_handler__(self) -> None:
        """ Все ответы сервера клиенту при подключении:
            "key-success"       - Значит что ключ подошёл, и клиент успешно присоединился к серверу.
            "key-error"         - Значит что ключ НЕ подошёл, и клиент был отключён.
            "key-timeout-error" - Значит что сервер слишком долго ждал получения ключа от клиента.
            "server-overflow"   - Значит что сервер переполнен, и присоединиться невозможно.
        """

        # Обрабатываем запросы на подключение:
        try:
            while True:
                try:
                    # Если мы останавливаем обработку присоединений:
                    if self.__netvars__["stop-handling"]: break

                    # Принимаем новое подключение клиента к серверу:
                    client, address = self.socket.accept()
                    client = NetSocket(client)

                    # Добавляем клиента в список клиентов только если на сервере есть свободные места:
                    if self.get_connect_count() < self.__netvars__["connect-limit"]:
                        # Но перед добавлением в список, проверяем ключ клиента:
                        try:
                            # Даём клиенту timeout времени, чтобы тот предоставил ключ:
                            client.set_time_out(self.__netvars__["timeout"])

                            # Получаем ключ и преобразовываем его:
                            client_key = client.recv_data(1024, "utf-8")
                            server_key = str(self.__netvars__["entry-key"])

                            # Проверяем ключ:
                            if client_key.strip() == server_key.strip():
                                # Если ключ правильный, то добавляем клиента в список:
                                self.__netvars__["clients"].append(client)

                                # Сообщаем клиенту, что тот прошёл:
                                client.send_data("key-success", "utf-8")

                                # Обрабатываем подключение клиента:
                                self.connect_handler(client, address)

                                # Создаём новый демонический поток для обработки клиента:
                                Thread(target=self.__client_handler__, args=(client, address), daemon=True).start()
                            else:
                                # Если ключ клиента не подходит, то сообщаем ему об этом, и отключаем от сервера:
                                client.send_data("key-error", "utf-8")
                                client.close()
                        except socket.timeout:
                            # Если клиент не успел предоставить ключ, то сообщаем ему об этом и отключаем его:
                            client.send_data("key-timeout-error", "utf-8")
                            client.close()
                    else:
                        # Если сервер переполнен:
                        client.send_data("server-overflow", "utf-8")
                        client.close()
                except socket.timeout:
                    raise NetTimeOut("[002] Connection Timeout. The client is not responding.")
                except OSError as error:
                    if error.errno == 10038:
                        raise NetException(
                            "[005] Server Error: An attempt was made to perform "
                            "an operation on an object that is not a socket")
                    else: raise NetException(f"[000] Unknown error (in NetServerTCP.__connect_handler__()): {error}")
        except Exception as error:
            raise NetException(f"[005] Server Error: {error}")
        finally: self.socket.close()

    # Создать сервер:
    def create(self,
               host:          str,
               port:          int,
               key:           str   = None,
               tps:           int   = 60,
               connect_limit: int   = 4,
               listen_limit:  int   = 4,
               timeout:       float = 10.0
               ) -> "NetServerTCP":
        # Подключаем сокет сервера к IP и порту:
        try: self.socket.bind(host, port)
        except OSError as error:
            if error.errno == 10049:
                raise NetException("[007] This address is invalid.")
            elif error.errno == 10048:
                raise NetException("[006] The selected Port is already occupied.")
            else: raise NetException(f"[000] Unknown error: {error}")
            self.socket.close()
            return self

        # Устанавливаем максимальное количество клиентов:
        self.set_connect_limit(max(int(connect_limit), 0))

        # Устанавливаем ограничение количества удерживаемых клиентов для подключения:
        self.set_listen_limit(max(int(listen_limit), 0))

        # Устанавливаем максимальное время ожидания ответа от клиента:
        self.set_timeout(timeout)

        # Ключ входа:
        self.__netvars__["entry-key"] = key.strip() if key is not None else None

        # TPS сервера:
        self.__netvars__["tps-limit"] = tps

        # Создаём новый демонический поток для обработки входящих подключений:
        Thread(target=self.__connect_handler__, args=(), daemon=True).start()

        return self

    # Установить максимальное количество поключаемых клиентов:
    def set_connect_limit(self, connect_limit: int) -> "NetServerTCP":
        self.__netvars__["connect-limit"] = connect_limit
        return self

    # Установить максимальное количество поключаемых клиентов:
    def set_listen_limit(self, listen_limit: int) -> "NetServerTCP":
        self.socket.listen(listen_limit)
        return self

    # Установить таймаута ожидания ответа:
    def set_timeout(self, timeout: float) -> "NetServerTCP":
        self.__netvars__["timeout"] = timeout
        return self

    # Получить количество соединений (клиентов):
    def get_connect_count(self) -> int:
        return len(self.__netvars__["clients"])

    # Получить ip сервера:
    def get_host(self) -> str:
        return self.socket.get_host()

    # Получить порт сервера:
    def get_port(self) -> int:
        return self.socket.get_port()

    # Отключить сервер (сеть):
    def destroy(self) -> None:
        self.__netvars__["stop-handling"] = True


# Класс клиента TCP/IP:
class NetClientTCP:
    def __init__(self, connect_handler: any, server_handler: any, disconnect_handler: any) -> None:
        # Внутренние переменные класса:
        self.connect_handler    = connect_handler     # Вызывается при подключении к серверу.
        self.server_handler     = server_handler      # Вызывается каждый 1/TPS раз в отдельном потоке.
        self.disconnect_handler = disconnect_handler  # Вызывается при отключении от сервера.
        self.__stop_handling__  = False               # Внутренний флаг для остановки обработки сервера.

        # Создаём сокет клиента (AF_INET это IPv4 | SOCK_STREAM это TCP):
        self.socket = NetSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    # Обработчик сервера в отдельном потоке:
    def __server_handler__(self, client: NetSocket, address: tuple) -> None:
        pass

    # Подключиться к серверу:
    def connect(self, host: str, port: int, key: str = None, timeout: float = 10.0) -> "NetClientTCP":
        # Устанавливаем тайм-аут на ожидание подтверждения подключения к серверу:
        self.socket.set_time_out(timeout+0.1)

        try:
            # Подключаемся к серверу:
            self.socket.connect(host, port)

            # Сразу отправляем ключ входа:
            self.socket.send_data(key, "utf-8")

            # Получаем ответ от сервера, прошли мы или нет:
            print(self.socket.recv_data(1024, "utf-8"))

        except socket.gaierror:
            self.socket.close()
            raise NetException("[004] The specified hostname does not exist or cannot be resolved.")
        except socket.timeout:
            self.socket.close()
            raise NetTimeOut("[002] Connection Timeout. Server too long to process the connection.")
        except ConnectionRefusedError:
            self.socket.close()
            raise NetConnectionRefused("[003] The server actively refuses to connect.")
        except OSError as error:
            self.socket.close()
            if error.errno == 10049:
                raise NetException("[001] Invalid server address (IP or Port)")
            else: raise NetException(f"[000] Unknown error: {error}")

        return self

    # Получить ip клиента:
    def get_host(self) -> str:
        return self.socket.get_host()

    # Получить порт клиента:
    def get_port(self) -> int:
        return self.socket.get_port()

    # Отключить клиента от сервера:
    def destroy(self) -> None:
        self.__stop_handling__ = True
        self.socket.close()
