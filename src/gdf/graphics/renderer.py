#
# renderer.py - Создаёт конвейер рендеринга, основанный на кадровых буферах.
#
# Вкратце, он нужен чтобы можно было рисовать всякие штуки при помощи OpenGL на одной текстуре, а после использовать
# эту текстуру как вам угодно. Renderer2D создаёт кадровый буфер и рисует на текстуре всё то что вам надо.
# Например, можно отрисовать результат шейдера на текстурке, как раз благодаря этому Renderer2D.
#
# Другими словами, этот класс нужен для простой работы с кадровыми буферами OpenGL.
#


# Импортируем:
if True:
    from .draw import Draw2D
    from .camera import Camera2D
    from .sprite import Sprite2D
    from .texture import Texture
    from .buffers import FrameBuffer


# Класс конвейера рендеринга 2D:
class Renderer2D:
    def __init__(self, camera: Camera2D) -> None:
        self.camera       = camera
        self.texture      = None
        self.framebuffer  = None
        self.sprite       = None
        self.__is_begin__ = False

        self.resize(self.camera.width, self.camera.height)

    # Начать рисовать на текстуре конвейера рендеринга:
    def begin(self) -> "Renderer2D":
        if self.__is_begin__:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self.__is_begin__  = True

        self.framebuffer.begin()
        return self

    # Закончить рисовать на текстуре конвейера рендеринга:
    def end(self) -> "Renderer2D":
        if self.__is_begin__: self.__is_begin__ = False
        else: raise Exception("The \".begin()\" function was not called before the \".end()\" function.")

        self.framebuffer.end()
        return self

    # Отрисовать текстурку конвейера рендеринга как спрайт, на весь экран:
    def render(self) -> "Renderer2D":
        if self.__is_begin__:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        self.camera.ui_begin()
        self.sprite.render(0, self.camera.height, self.camera.width, -self.camera.height)
        self.camera.ui_end()
        return self

    # Закрасить кадровый буфер:
    def fill(self, color: list = None) -> "Renderer2D":
        if color is None: color = [0, 0, 0, 1]

        self.begin()
        self.camera.ui_begin()
        w, h = self.camera.width, self.camera.height
        Draw2D.quads([0, 0, 0, 1], [(0, 0), (+w, 0), (+w, +h), (0, +h)])
        Draw2D.quads(color       , [(0, 0), (+w, 0), (+w, +h), (0, +h)])
        self.camera.ui_end()
        self.end()

        return self

    # Изменить размер текстурки конвейера рендеринга:
    def resize(self, width: int, height: int) -> "Renderer2D":
        # Останавливаем использование кадрового буфера:
        if self.__is_begin__: self.end()

        # Пересоздаём текстурку кадрового буфера:
        if self.texture is not None: self.texture.destroy() ; self.texture = None
        if self.texture is     None: self.texture = Texture(None, size=(width, height))

        # Пересоздаём кадровый буфер, так как скорее всего, id текстуры уже другой:
        if self.framebuffer is not None: self.framebuffer.destroy() ; self.framebuffer = None
        if self.framebuffer is     None: self.framebuffer = FrameBuffer(self.texture.id)

        self.sprite = Sprite2D(self.texture)
        return self

    # Удалить конвейер рендеринга:
    def destroy(self) -> None:
        self.framebuffer.destroy()
        self.texture.destroy()
