#
# renderer.py - Создаёт конвейер рендеринга, основанный на кадровых буферах.
#
# Вкратце, он нужен чтобы можно было рисовать всякие штуки при помощи OpenGL на одной текстуре, а после использовать
# эту текстуру как вам угодно. Renderer2D создаёт кадровый буфер и рисует на текстуре всё то что вам надо.
#
# Другими словами, этот класс нужен для простой работы с кадровыми буферами OpenGL.
#


# Импортируем:
from .gl import *
from .draw import Draw2D
from .camera import Camera2D
from .sprite import Sprite2D
from .texture import Texture
from .buffers import FrameBuffer


# Класс конвейера рендеринга 2D:
class Renderer2D:
    def __init__(self, camera: Camera2D, width: int = None, height: int = None) -> None:
        if width is not None and height is not None:
            wdth, hght = int(width), int(height)
        elif camera is not None:
            wdth, hght = camera.width, camera.height

        self.camera      = camera
        self.texture     = Texture(None, size=(wdth, hght))
        self.framebuffer = FrameBuffer(self.texture)
        self.sprite      = Sprite2D(self.texture)
        self._is_begin_  = False

    # Начать рисовать на текстуре конвейера рендеринга:
    def begin(self) -> "Renderer2D":
        if self._is_begin_:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._is_begin_ = True

        self.framebuffer.begin()
        return self

    # Закончить рисовать на текстуре конвейера рендеринга:
    def end(self) -> "Renderer2D":
        if self._is_begin_: self._is_begin_ = False
        else: raise Exception("The \".begin()\" function was not called before the \".end()\" function.")

        self.framebuffer.end()
        return self

    # Отрисовать текстурку конвейера рендеринга как спрайт, на весь экран:
    def render(self) -> "Renderer2D":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        self.camera.ui_begin()
        self.sprite.render(0, self.texture.height, self.texture.width, -self.texture.height)
        self.camera.ui_end()
        return self

    # Отрисовать шейдер на всей текстуре:
    def render_shader(self, color: list = None) -> None:
        if color is None: color = [1, 1, 1]
        Draw2D.triangle_fan(color, [(-1, -1), (+1, -1), (+1, +1), (-1, +1)])

    # Очистить кадровый буфер:
    def clear(self, color: list = None) -> "Renderer2D":
        self.framebuffer.clear(color)
        return self

    # Изменить размер текстурки конвейера рендеринга:
    def resize(self, width: int, height: int) -> "Renderer2D":
        # Останавливаем использование кадрового буфера:
        if self._is_begin_: self.end()

        self.framebuffer.resize(int(width), int(height))
        return self

    # Удалить конвейер рендеринга:
    def destroy(self) -> None:
        self.framebuffer.destroy()
        self.texture.destroy()
