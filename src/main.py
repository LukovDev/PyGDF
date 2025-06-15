#
# main.py - Основной запускаемый файл программы.
#


# Импортируем:
import gdf
from gdf import files
from gdf.math import *
from gdf.input import InputHandler, Key
from gdf.graphics import *  # Window, Camera2D, Sprite2D
from gdf.graphics.gl import *
from gdf.utils import Utils2D


# Класс игры:
class GameClass(Window):
    def __init__(self) -> None:
        self.input  = None  # Обработчик ввода.
        self.camera = None  # Игровая камера.
        self.sprite = None  # Наш спрайт.

        # Создаём окно и переходим в игровой цикл:
        self.init()

    # Создать окно:
    def init(self) -> None:
        super().__init__(
            title      = "PyGDF Window",
            icon       = files.load_image("data/icons/runapp-icon.png"),
            size       = vec2(960, 540),
            vsync      = False,
            fps        = 100000,
            visible    = True,
            titlebar   = True,
            resizable  = True,
            fullscreen = False,
            min_size   = vec2(0, 0),
            max_size   = vec2(float("inf"), float("inf")),
            samples    = 16  # 0 / 2 / 4 / 8 / 16 - MultiSampling (Anti-Aliasing).
        )

    # Вызывается при создании окна:
    def start(self) -> None:
        # Наш обработчик ввода данных:
        self.input = InputHandler(self.window)

        # 2D камера:
        self.camera = Camera2D(
            width    = self.window.get_width(),
            height   = self.window.get_height(),
            position = vec2(0, 0),
        )

        self.controller = gdf.controllers.CameraController2D(self.input, self.camera)

        # Загружаем текстуру, которую укажем в нашем спрайте чтобы её отрисовать:
        texture = files.load_texture("data/icons/runapp-icon.png")

        self.texture1 = files.load_texture("data/icons/runapp-icon.png")
        self.texture2 = files.load_texture("data/icons/boom.png").set_pixelized()

        # Наш спрайт. Принимает текстуру, которую будет отрисовывать:
        self.sprite = Sprite2D(texture)
        self.sprite2 = Sprite2D(self.texture2)

        self.batch = SpriteBatch()

    # Вызывается каждый кадр (игровой цикл):
    def update(self, delta_time: float, event_list: list) -> None:
        # Какой-то код (логика).

        # Обновляем камеру:
        self.controller.update(delta_time)
        self.camera.update()

    # Вызывается каждый кадр (игровая отрисовка):
    def render(self, delta_time: float) -> None:
        # Очищаем окно (значения цвета от 0 до 1):
        self.window.clear(0.1, 0.1, 0.1)

        # Какой-то код (отрисовка).
        # self.sprite.render(x=0, y=0, width=64, height=64, angle=0)
        t = self.window.get_time()
        color = vec3(sin(t)*0.5+0.5, sin(t+2.0)*0.5+0.5, sin(t+4.0)*0.5+0.5)
        self.sprite2.render(x=128, y=0, width=128, height=128, angle=sin(self.window.get_time())*180, color=color)

        self.batch.begin()
        for i in range(8192):
            self.batch.draw(self.sprite, 0, i*100, 100, 100)
        self.batch.end()
        self.batch.render()

        #SimpleDraw.circle(vec3(1, 0, 0), vec2(-100), 100)

        """
        1. переделать пакетную отрисовку под новый опенгл.
        2. Починить баг с системой частиц на низком фпс.
        3. Обновить работу с атласами текстур и упаковщиком текстур и сделать загрузку отдельной конфигурации для атласа текстур.
        4. Добавить поддержку джостика.
        5. Сделать поддержку воспроизведения медиа (видео/гиф).
        6. Сделать модуль AI для поиска пути по 2д тайлам.
        7. Сделать добавление текстурки/изображения в генератор текстуры с текстом под видом спец-символа.
        8. Написать тесты ядра для проверки всего функционала и проверки на баги
        9. Сделать документацию.
        10. Сделать релиз и проверить все изменения и написать готовый список изменений и тд.
        """

        # Отрисовываем всё в окно:
        self.window.display()

    # Вызывается при изменении размера окна:
    def resize(self, width: int, height: int) -> None:
        self.camera.resize(width, height)  # Обновляем размер камеры.

    # Вызывается при разворачивании окна:
    def show(self) -> None:
        pass

    # Вызывается при сворачивании окна:
    def hide(self) -> None:
        pass

    # Вызывается при закрытии окна:
    def destroy(self) -> None:
        self.sprite.destroy()  # Удаляем текстуру в спрайте, чтобы освободить ресурсы.


# Если этот скрипт запускают:
if __name__ == "__main__":
    # Выводим текущую версию фреймворка:
    print(f"PyGDF: {gdf.get_version()}\n")

    # Создаём игровой класс:
    game = GameClass()
