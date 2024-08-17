#
# tcpip.py - TCP/IP реализация интернет соединения. Реализует класс для передачи данных через TCP/IP протокол.
#


# Импортируем:
import time
import errno
from threading import Thread
from . import *


# Класс сервера TCP/IP:
class NetServerTCP:
    """ Пример функций-обработчиков:

    # Вызывается при присоединении клиента:
    def connect_handler(socket: NetSocket, address: tuple) -> None:
        pass

    # Вызывается каждый цикл обработки:
    def socket_handler(socket: NetSocket, address: tuple, delta_time: float) -> None:
        ...

    # Вызывается при отсоединении клиента:
    def disconnect_handler(socket: NetSocket, address: tuple) -> None:
        pass

    # Вызывается при получении ошибки в обработчике клиента:
    def error_handler(error: NetException | str, address: tuple) -> None:
        pass
    """

    # Инициализация:
    def __init__(self, connect_handler: any, socket_handler: any, disconnect_handler: any, error_handler: any) -> None:
        # Внутренние переменные класса:
        self.connect_handler    = connect_handler     # Вызывается при подключении клиента.
        self.socket_handler     = socket_handler      # Вызывается каждый цикл обработки.
        self.disconnect_handler = disconnect_handler  # Вызывается при отключении клиента.
        self.error_handler      = error_handler       # Вызывается при получении ошибки в обработчике клиента.

        # Внутренние переменные:
        self._netvars_ = {
            "clients":       [],      # Список клиентов.
            "connect-limit": int,     # Максимальное количество клиентов.
            "entry-key":     str,     # Ключ входа.
            "tps-limit":     float,   # Частота цикла обработки клиента (сколько раз в сек обработать).
            "timeout":       float,   # Время ожидания ответа между клиентом и сервером.
            "de-encoding":   "utf-8"  # Кодировка обменивания личными сообщениями между клиентом и сервером.
        }

        # Создаём сокет сервера (AF_INET это IPv4 | SOCK_STREAM это TCP):
        self.socket = NetSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    # Обработчик клиентов в отдельном потоке:
    def _client_handler_(self, client: NetSocket, address: tuple) -> None:
        try:
            # Дельта времени:
            dtime = 1 / self._netvars_["tps-limit"]

            # Установка таймаута на ожидание ответа от клиента:
            client.set_time_out(self._netvars_["timeout"])

            # Обрабатываем подключение клиента:
            self.connect_handler(client, address)

            while True:
                # Время начала цикла:
                stime = time.time()

                try:
                    # Смотрим данные, если есть пустое сообщение, то сокет отсоединился:
                    try:
                        client.set_blocking(False)
                        if not client.socket.recv(1, socket.MSG_PEEK): break
                    except BlockingIOError: pass
                    finally: client.set_blocking(True)

                    # Обрабатываем сокет:
                    self.socket_handler(client, address, dtime)

                    # Проверка накопленного времени таймаута:
                    if time.time() - stime > self._netvars_["timeout"]:
                        self.error_handler(NetConnectionTimeout.__name__, address) ; break
                except (OSError, TypeError, socket.error):
                    break  # Выходим из за ошибки с работой сокета.

                # Делаем некоторую задержку между циклом, чтобы не взорвать провайдера:
                dtps, timeout = 1 / self._netvars_["tps-limit"], self._netvars_["timeout"]
                time.sleep(dtps if dtps < timeout else timeout)  # DTPS не может быть больше таймаута.

                # Обновляем дельту времени:
                dtime = time.time() - stime

        except (TimeoutError, socket.timeout):
            self.error_handler(NetConnectionTimeout.__name__, address)

        except ConnectionAbortedError:
            self.error_handler(NetConnectionAborted.__name__, address)

        except ConnectionResetError:
            self.error_handler(NetConnectionResetError.__name__, address)

        except BrokenPipeError:
            self.error_handler(NetBrokenPipeError.__name__, address)

        except Exception as error:
            self.error_handler(f"{NetConnectionLost.__name__}: {error}", address)

        finally:
            # Обрабатываем отключение клиента:
            self.disconnect_handler(client, address)

            # Удаляем этого клиента из списка:
            self._netvars_["clients"].remove(client) if client in self._netvars_["clients"] else None

            # Закрываем сокет клиента (соединение с клиентом) в любом случае:
            client.close()

    # Обработчик присоединений клиентов к серверу:
    def _connect_handler_(self) -> None:
        # Обрабатываем запросы на подключение:
        try:
            # Метаданные отправляемые ответом сервера на подключение:
            metadata = {
                "pcsc-version": TCP_PCSC_VERSION
            }

            # Функция для преобразования простых данных в пакет данных для отправки:
            send_package = lambda c, d: c.send_json({"data": d, "meta": metadata}, self._netvars_["de-encoding"])

            # Вечный цикл:
            while True:
                try:
                    # Принимаем новое подключение клиента к серверу:
                    try: client, address = self.socket.accept()
                    except OSError as error: break
                    client = NetSocket(client)

                    # Добавляем клиента в список клиентов только если сервер не переполнен:
                    if self.get_connect_count() < self._netvars_["connect-limit"]:
                        # Но перед регистрации клиента, проверяем его ключ:
                        try:
                            # Даём клиенту timeout времени, чтобы тот предоставил ключ:
                            client.set_time_out(self._netvars_["timeout"])

                            # Получаем ключ и преобразовываем его в нормальный формат для ключей:
                            client_key = client.recv_data(1024, self._netvars_["de-encoding"]).strip()
                            server_key = str(self._netvars_["entry-key"]).strip()

                            # Проверяем ключ:
                            if client_key == server_key:
                                # Если ключ правильный, то регистрируем клиента на сервере.

                                # Сообщаем клиенту, что тот прошёл:
                                send_package(client, str(0x00))

                                # Добавляем его в список клиентов на сервере:
                                self._netvars_["clients"].append(client)

                                # Создаём новый демонический поток для обработки клиента:
                                Thread(target=self._client_handler_, args=(client, address), daemon=True).start()
                            else:
                                # Если ключ клиента не подходит, то сообщаем ему об этом, и отключаем от сервера:
                                send_package(client, str(NetClientKeyWrong.id_error))
                                client.close()
                        except socket.timeout:
                            # Если клиент не успел предоставить ключ, то сообщаем ему об этом и отключаем его:
                            send_package(client, str(NetClientKeyTimeout.id_error))
                            client.close()
                    else:
                        # Если сервер переполнен:
                        send_package(client, str(NetServerOverflow.id_error))
                        client.close()
                except (OSError, socket.timeout):
                    client.close()  # При любой непонятной ошибке, просто отключаем клиента.
        except Exception as error:
            # Вызываем критическую ошибку при обработке входящих подключений:
            raise NetException(error)
        finally: self.socket.close()

    # Создать сервер:
    def create(self,
               host:          str,
               port:          int,
               key:           str   = None,
               tps:           float = 60.0,
               connect_limit: int   = 4,
               listen_limit:  int   = 4,
               timeout:       float = 10.0
               ) -> "NetServerTCP":
        # Подключаем сокет сервера к IP и порту:
        try: self.socket.bind(host, port)
        except OSError as error:
            self.socket.close()
            if error.errno == 10049 or error.errno == 10048:
                raise NetAddressInvalid()
            elif error.errno == errno.ENETUNREACH:
                raise NetUnavailable()
            elif error.errno == errno.EHOSTUNREACH:
                raise NetHostUnreachable()
            else:
                raise NetOSError(error)

        # Устанавливаем максимальное количество клиентов:
        self.set_connect_limit(max(int(connect_limit), 0))

        # Устанавливаем ограничение количества удерживаемых клиентов для подключения:
        self.set_listen_limit(max(int(listen_limit), 0))

        # Устанавливаем максимальное время ожидания ответа от клиента:
        self.set_timeout(timeout)

        # Ключ входа:
        self._netvars_["entry-key"] = key.strip() if key is not None else None

        # TPS сервера:
        self._netvars_["tps-limit"] = tps

        # Создаём новый демонический поток для обработки входящих подключений:
        Thread(target=self._connect_handler_, args=(), daemon=True).start()

        return self

    # Установить максимальное количество поключаемых клиентов:
    def set_connect_limit(self, connect_limit: int) -> "NetServerTCP":
        self._netvars_["connect-limit"] = connect_limit
        return self

    # Установить максимальное количество поключаемых клиентов:
    def set_listen_limit(self, listen_limit: int) -> "NetServerTCP":
        self.socket.listen(listen_limit)
        return self

    # Установить таймаута ожидания ответа:
    def set_timeout(self, timeout: float) -> "NetServerTCP":
        self._netvars_["timeout"] = timeout
        return self

    # Получить список клиентов:
    def get_connects(self) -> list:
        return self._netvars_["clients"]

    # Получить количество соединений (клиентов):
    def get_connect_count(self) -> int:
        return len(self.get_connects())

    # Получить ip сервера:
    def get_host(self) -> str:
        return self.socket.get_host()

    # Получить порт сервера:
    def get_port(self) -> int:
        return self.socket.get_port()

    # Отключить всех клиентов:
    def disconnect_all(self) -> "NetServerTCP":
        # Отключаем всех клиентов и очищаем список клиентов:
        for c in list(self._netvars_["clients"]): c.close()
        self._netvars_["clients"].clear()

        return self

    # Отключить сервер (сеть):
    def destroy(self) -> None:
        # Отключаем всех клиентов и останавливаем сервер:
        self.disconnect_all()
        self.socket.close()


# Класс клиента TCP/IP:
class NetClientTCP:
    """ Пример функций-обработчиков:

    # Вызывается при присоединении к серверу:
    def connect_handler(socket: NetSocket, address: tuple) -> None:
        pass

    # Вызывается каждый цикл обработки:
    def socket_handler(socket: NetSocket, address: tuple, delta_time: float) -> None:
        ...

    # Вызывается при потери связи с сервером:
    def disconnect_handler(socket: NetSocket, address: tuple) -> None:
        pass

    # Вызывается при получении ошибки в обработчике сервера:
    def error_handler(error: NetException | str, address: tuple) -> None:
        pass
    """

    # Инициализация:
    def __init__(self, connect_handler: any, socket_handler: any, disconnect_handler: any, error_handler: any) -> None:
        # Внутренние переменные:
        self.connect_handler    = connect_handler     # Вызывается при подключении к серверу.
        self.socket_handler     = socket_handler      # Вызывается каждый 1/TPS раз в отдельном потоке.
        self.disconnect_handler = disconnect_handler  # Вызывается при отключении от сервера.
        self.error_handler      = error_handler       # Вызывается при получении ошибки в обработчике сервера.

        self._netvars_ = {
            "tps-limit":    float,    # Частота цикла обработки сервера (сколько раз в сек обработать).
            "timeout":      float,    # Время ожидания ответа между клиентом и сервером.
            "de-encoding":  "utf-8",  # Кодировка обменивания личными сообщениями между клиентом и сервером.
            "disconnected": False,    # Надо чтобы лишний раз не вызывать функцию отключения.
        }

        # Создаём сокет клиента (AF_INET это IPv4 | SOCK_STREAM это TCP):
        self.socket = NetSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    # Обработчик сервера в отдельном потоке:
    def _server_handler_(self, server: NetSocket, address: tuple) -> None:
        try:
            # Дельта времени:
            dtime = 1 / self._netvars_["tps-limit"]

            # Установка таймаута на ожидание ответа от сервера:
            server.set_time_out(self._netvars_["timeout"])

            # Обрабатываем подключение:
            self.connect_handler(server, address)

            while True:
                # Время начала цикла:
                stime = time.time()
                
                try:
                    # Смотрим данные, если есть пустое сообщение, то сокет отсоединился:
                    try:
                        server.set_blocking(False)
                        if not server.socket.recv(1, socket.MSG_PEEK): break
                    except BlockingIOError: pass
                    finally: server.set_blocking(True)

                    # Обрабатываем сокет:
                    self.socket_handler(server, address, dtime)

                    # Проверка накопленного времени таймаута:
                    if time.time() - stime > self._netvars_["timeout"]:
                        self.error_handler(NetConnectionTimeout.__name__, address) ; break
                except (OSError, TypeError, socket.error):
                    break  # Выходим из за ошибки с работой сокета.

                # Делаем некоторую задержку между циклом, чтобы не взорвать провайдера:
                dtps, timeout = 1 / self._netvars_["tps-limit"], self._netvars_["timeout"]
                time.sleep(dtps if dtps < timeout else timeout)  # DTPS не может быть больше таймаута.
                
                # Обновляем дельту времени:
                dtime = time.time() - stime

        except (TimeoutError, socket.timeout):
            self.error_handler(NetConnectionTimeout.__name__, address)

        except ConnectionAbortedError:
            self.error_handler(NetConnectionAborted.__name__, address)

        except ConnectionResetError:
            self.error_handler(NetConnectionResetError.__name__, address)

        except BrokenPipeError:
            self.error_handler(NetBrokenPipeError.__name__, address)

        except Exception as error:
            self.error_handler(f"{NetConnectionLost.__name__}: {error}", address)

        finally:
            self.disconnect()

    # Подключиться к серверу:
    def connect(self,
                host:    str,
                port:    int,
                key:     str   = None,
                tps:     float = 60.0,
                timeout: float = 10.0
                ) -> "NetClientTCP":
        # Устанавливаем тайм-аут на ожидание подтверждения подключения к серверу:
        self.socket.set_time_out(timeout)

        try:
            # Подключаемся к серверу:
            self.socket.connect(host, port)
            serv_addr = self.socket.get_peer_name()

            # Сразу отправляем ключ входа:
            self.socket.send_data(key, self._netvars_["de-encoding"])

            # Получаем ответ от сервера:
            rec = self.socket.recv_json(1024, self._netvars_["de-encoding"])
            data, meta = rec["data"], rec["meta"]  # Делим ответ на ответ подключения и на прочую служебную информацию.

            # Проверяем версию протокола подключения:
            if meta["pcsc-version"] != TCP_PCSC_VERSION:
                raise NetException(
                     "Connection was not established: Different versions of the Protocol Connection Server-Client.\n"
                    f"You PCSC version: \"{TCP_PCSC_VERSION}\", Server PCSC version: \"{meta['pcsc-version']}\"\n"
                )

            # Проверка полученного ответа от сервера на подключение по протоколу подключения сервер-клиент:

            # Если ключ не правильный:
            if int(data) == NetClientKeyWrong.id_error:
                self.socket.close()
                raise NetClientKeyWrong()

            # Иначе если время за которое мы должны были отправить ключ, вышло:
            elif int(data) == NetClientKeyTimeout.id_error:
                self.socket.close()
                raise NetClientKeyTimeout()

            # Иначе если сервер переполнен:
            elif int(data) == NetServerOverflow.id_error:
                self.socket.close()
                raise NetServerOverflow()

            # Иначе если ключ правильный:
            elif int(data) == 0x00:
                # Устанавливаем максимальное время ожидания ответа от сервера:
                self.set_timeout(timeout)

                # Обнуляем флаг вызова отключения:
                self._netvars_["disconnected"] = False

                # TPS клиента:
                self._netvars_["tps-limit"] = tps

                # Создаём новый демонический поток для обработки сервера:
                Thread(target=self._server_handler_, args=(self.socket, serv_addr), daemon=True).start()
            else:
                raise NetException(f"Connection was not established for an unknown reason: \"{data}\"")

        except socket.gaierror:
            self.socket.close()
            raise NetAddressRelatedError()

        except (TimeoutError, socket.timeout):
            self.socket.close()
            raise NetConnectingTimedOut()

        except ConnectionRefusedError:
            self.socket.close()
            raise NetConnectingRefused()

        except ConnectionAbortedError:
            self.socket.close()
            raise NetConnectingAborted()

        except ConnectionResetError:
            self.socket.close()
            raise NetConnectingResetError()

        except OSError as error:
            self.socket.close()
            if error.errno == 10049:
                raise NetAddressInvalid()
            elif error.errno == errno.ENETUNREACH:
                raise NetUnavailable()
            elif error.errno == errno.EHOSTUNREACH:
                raise NetHostUnreachable()
            else:
                raise NetOSError(error)

        return self

    # Установить таймаута ожидания ответа:
    def set_timeout(self, timeout: float) -> "NetClientTCP":
        self._netvars_["timeout"] = timeout
        return self

    # Получить ip клиента:
    def get_host(self) -> str:
        return self.socket.get_host()

    # Получить порт клиента:
    def get_port(self) -> int:
        return self.socket.get_port()

    # Отключаемся от сервера:
    def disconnect(self) -> "NetClientTCP":
        # Устанавливаем флаг отключения, чтобы лишний раз эта функция не вызывалась:
        if not self._netvars_["disconnected"]:
            self._netvars_["disconnected"] = True
        else: return self  # Если же эту функцию вызвали насильно, то просто ничего не делаем.

        # Обрабатываем отключение от сервера:
        self.disconnect_handler(self.socket, self.socket.get_peer_name())

        # Закрываем сокет клиента (соединение с клиентом) в любом случае:
        self.socket.close()

        return self

    # Отключить клиента от сервера:
    def destroy(self) -> None:
        self.disconnect()
