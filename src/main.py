#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
if True:
    # Ядро фреймворка:
    import lgfw
    from lgfw import files
    from lgfw.math import *
    from lgfw.graphics import Window, Camera2D, Sprite


# Класс игры:
class GameClass(Window):
    def __init__(self) -> None:
        self.camera = None  # Игровая камера.
        self.sprite = None  # Наш спрайт.

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

        # Загружаем текстуру, которую укажем в нашем спрайте чтобы её отрисовать:
        texture = files.load_texture("./data/icons/runapp-icon.png")

        # Наш спрайт. Принимает текстуру, которую будет отрисовывать:
        self.sprite = Sprite(texture)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, events: list) -> None:
        # Очищаем окно (значения цвета от 0 до 1):
        self.window.clear(0, 0, 0)

        # Отрисовываем наш спрайт (width и height можно убрать и тогда будет использоваться размер текстуры):
        self.sprite.render(x=-64, y=-64, width=128, height=128)

        # Отрисовываем всё в окно:
        self.window.display()

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
    version = lgfw.get_version()
    print(f"LibGFW version: {version}")

    game = GameClass()
