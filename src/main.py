#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
if True:
    # Ядро фреймворка:
    import gdf
    from gdf import files
    from gdf.math import *
    from gdf.graphics import Window, Camera2D, Sprite2D


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
            title      = "PyGDF Window",
            icon       = files.load_image("./data/icons/runapp-icon.png"),
            size       = vec2(960, 540),
            vsync      = False,
            fps        = 60,
            visible    = True,
            fullscreen = False,
            min_size   = vec2(0, 0),
            max_size   = vec2(float("inf"), float("inf")),
            samples    = 16  # [ 0 | 4 | 8 | 16 ]
        )

    # Вызывается при создании окна:
    def start(self) -> None:
        # Выводим версию OpenGL:
        print(f"OpenGL Version: {self.window.get_opengl_version()}\n")

        # Выводим рендерер OpenGL:
        print(f"OpenGL Renderer: {self.window.get_opengl_renderer()}\n")

        # 2D камера:
        self.camera = Camera2D(
            width    = self.window.get_width(),
            height   = self.window.get_height(),
            position = vec2(0, 0),
            angle    = 0.0,
            zoom     = 1.0
        )

        # Загружаем текстуру, которую укажем в нашем спрайте чтобы её отрисовать:
        texture = files.load_texture("./data/icons/runapp-icon.png")

        # Наш спрайт. Принимает текстуру, которую будет отрисовывать:
        self.sprite = Sprite2D(texture)

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        for event in event_list:
            # События окна.
            pass

        # Какой-то код (логика).

        # Рисуем всё в окно:
        self.render(delta_time)

    # Вызывается в конце функции update чтобы отрисовать все изменения:
    def render(self, delta_time: float) -> None:
        # Очищаем окно (значения цвета от 0 до 1):
        self.window.clear(0, 0, 0)

        # Какой-то код (отрисовка).

        # Обновляем камеру:
        self.camera.update()

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
    print(f"PyGDF: {gdf.get_version()}\n")

    # Выводим название платформы:
    print(f"Platform: {gdf.get_platform()}\n")

    game = GameClass()
