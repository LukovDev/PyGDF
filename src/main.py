#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
if True:
    # Ядро фреймворка:
    import core
    from core import files
    from core.math import *
    from core.graphics import Window, Camera2D


# Класс игры:
class GameClass(Window):
    def __init__(self) -> None:
        self.camera = None   # Игровая камера.

        # Создаём окно и переходим в игровой цикл:
        self.init()

    # Создать окно:
    def init(self) -> None:
        super().__init__(
            title      = "LibGFW Window",                                   # Заголовок окна.
            icon       = files.load_image("./data/icons/runapp-icon.png"),  # Заголовочная иконка окна.
            size       = (960, 540),                                        # Размер окна.
            vsync      = False,                                             # Вертикальная синхронизация.
            fps        = 60,     # Количество кадров в секунду (т.е. количество игровых циклов в секунду).
            visible    = True,   # Отображаемость окна.
            fullscreen = False,  # Окно на весь экран (разрешение экрана изменится на размер окна).
            min_size   = (0, 0),                                            # Минимальный размер окна.
            max_size   = (float("inf"), float("inf"))                       # Максимальный размер окна.
        )

    # Вызывается при создании окна:
    def start(self) -> None:
        # 2D камера:
        self.camera = Camera2D(
            width    = self.window.get_size()[0],  # Ширина камеры.
            height   = self.window.get_size()[1],  # Высота камеры.
            position = vec2(0, 0),                 # Позиция камеры.
            angle    = 0.0,                        # Угол наклона камеры.
            zoom     = 1.0                         # Масштаб камеры.
        )

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, events: list) -> None:

        # Тут игровая логика.

        self.window.clear(0, 0, 0) # Очищаем окно (значения цвета от 0 до 1 R-G-B).

        # Тут отрисовка игры.

        self.window.display()  # Отрисовываем всё в окно.

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        self.camera.resize(width, height)

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        pass


# Если этот скрипт запускают:
if __name__ == "__main__":

    # Выводим текущую версию фреймворка:
    version = core.get_version()
    print(f"LibGFW version: {version}")

    game = GameClass()
