#
# render.py - Создаёт классы для работы с рендерингом чего-либо.
#


# Импортируем:
from .gl import *
from .shader import ShaderProgram
from .texture import Texture
from .buffers import *
from ..math import *


# Класс с базовыми шейдерами для рендеринга:
class RenderPipeline:
    camera = None  # Текущая активная камера.

    # Шейдер по умолчанию:
    default_shader: ShaderProgram = ShaderProgram(
        vert="""
            #version 330 core

            uniform mat4 u_model = mat4(1.0);
            uniform mat4 u_view = mat4(1.0);
            uniform mat4 u_projection = mat4(1.0);
            layout (location = 0) in vec3 a_position;
            layout (location = 1) in vec2 a_texcoord;
            out vec2 TexCoord;

            void main(void) {
                gl_Position = u_projection * u_view * u_model * vec4(a_position, 1.0);
                TexCoord = a_texcoord;
            }
        """,
        frag="""
            #version 330 core

            uniform bool u_use_points = false;
            uniform bool u_use_texture;
            uniform vec4 u_color = vec4(1.0);
            uniform sampler2D u_texture;
            in vec2 TexCoord;
            out vec4 FragColor;

            void main(void) {
                // Если мы используем точки для рисования:
                if (u_use_points) {
                    vec2 coord = gl_PointCoord*2.0-1.0;
                    if (dot(coord, coord) > 1.0) discard;  // Отбрасываем всё за пределами круга.
                }
                // Если мы используем текстуру, рисуем с ней, иначе только цвет:
                if (u_use_texture) {
                    FragColor = u_color * texture(u_texture, TexCoord);
                } else {
                    FragColor = u_color;
                }
            }
        """
    )

    # Скайбокс:
    class Skybox:
        # Кубическое небо:
        class CubeMap:
            # Вершины (1 сторона = 2 треугольника):
            vertices: list = [
                (-1, +1, +1),  (+1, +1, +1),  (+1, -1, +1), (+1, -1, +1),  (-1, -1, +1),  (-1, +1, +1),  # Front.
                (+1, +1, -1),  (-1, +1, -1),  (-1, -1, -1), (-1, -1, -1),  (+1, -1, -1),  (+1, +1, -1),  # Back.
                (-1, +1, -1),  (-1, +1, +1),  (-1, -1,  1), (-1, -1, +1),  (-1, -1, -1),  (-1, +1, -1),  # Left.
                (+1, +1, +1),  (+1, +1, -1),  (+1, -1, -1), (+1, -1, -1),  (+1, -1, +1),  (+1, +1, +1),  # Right.
                (-1, +1, -1),  (+1, +1, -1),  (+1, +1,  1), (+1, +1, +1),  (-1, +1, +1),  (-1, +1, -1),  # Top.
                (+1, -1, +1),  (+1, -1, -1),  (-1, -1, -1), (-1, -1, -1),  (-1, -1, +1),  (+1, -1, +1),  # Bottom.
            ]

            # Текстурные координаты:
            texcoords: list = [
                (0, 0), (1, 0), (1, 1), (1, 1), (0, 1), (0, 0),  # Front.
                (0, 0), (1, 0), (1, 1), (1, 1), (0, 1), (0, 0),  # Back.
                (0, 0), (1, 0), (1, 1), (1, 1), (0, 1), (0, 0),  # Left.
                (0, 0), (1, 0), (1, 1), (1, 1), (0, 1), (0, 0),  # Right.
                (0, 0), (1, 0), (1, 1), (1, 1), (0, 1), (0, 0),  # Top.
                (1, 0), (1, 1), (0, 1), (0, 1), (0, 0), (1, 0),  # Bottom.
            ]

            # Буфер вершин:
            vvbo: VBO = None

            # Буфер текстурных координат:
            tvbo: VBO = None

            # Буфер атрибутов:
            vao: VAO = None

            # Функция ручной инициализации:
            @staticmethod
            def _init_() -> None:
                # Создаём общие буферы:
                verts, texcoord = RenderPipeline.Skybox.CubeMap.vertices, RenderPipeline.Skybox.CubeMap.texcoords
                RenderPipeline.Skybox.CubeMap.vvbo = VBO(np.array(verts, dtype=np.float32), None, gl.GL_STATIC_DRAW)
                RenderPipeline.Skybox.CubeMap.tvbo = VBO(np.array(texcoord, dtype=np.float32), None,  gl.GL_STATIC_DRAW)
                RenderPipeline.Skybox.CubeMap.vao = VAO()

                # Устанавливаем атрибуты vao:
                RenderPipeline.Skybox.CubeMap.vao.begin()   # Используем VAO.
                RenderPipeline.Skybox.CubeMap.vvbo.begin()  # Используем VBO сетку.
                RenderPipeline.Skybox.CubeMap.vao.attrib_pointer(location=0, count=3)  # Вершина состоит из трёх чисел.
                RenderPipeline.Skybox.CubeMap.vvbo.end()    # Не используем VBO сетку.
                RenderPipeline.Skybox.CubeMap.tvbo.begin()  # Используем VBO текстурных координат.
                RenderPipeline.Skybox.CubeMap.vao.attrib_pointer(location=1, count=2)  # А координаты из двух чисел.
                RenderPipeline.Skybox.CubeMap.tvbo.end()    # Не используем VBO текстурных координат.
                RenderPipeline.Skybox.CubeMap.vao.end()     # Не используем VAO.

    # Простая отрисовка:
    class SimpleDraw:
        # Буфер вершин:
        vvbo: VBO = None

        # Буфер атрибутов:
        vao: VAO = None

        # Функция ручной инициализации:
        @staticmethod
        def _init_() -> None:
            # Создаём общие буферы:
            RenderPipeline.SimpleDraw.vvbo = VBO(np.array([], dtype=np.float32), None, gl.GL_DYNAMIC_DRAW)
            RenderPipeline.SimpleDraw.vao = VAO()

            # Устанавливаем атрибуты vao:
            RenderPipeline.SimpleDraw.vao.begin()   # Используем VAO.
            RenderPipeline.SimpleDraw.vvbo.begin()  # Используем VBO.
            RenderPipeline.SimpleDraw.vao.attrib_pointer(location=0, count=3)  # Вершина состоит из трёх чисел.
            RenderPipeline.SimpleDraw.vvbo.end()    # Не используем VBO.
            RenderPipeline.SimpleDraw.vao.end()     # Не используем VAO.

    # Спрайт:
    class Sprite:
        # Вершины (2 треугольника):
        vertices: list = [(-1, -1, 0), (+1, -1, 0), (+1, +1, 0), (-1, +1, 0)]

        # Текстурные координаты:
        texcoords: list = [(+0, +1), (+1, +1), (+1, +0), (+0, +0)]

        # Буфер вершин:
        vvbo: VBO = None

        # Буфер текстурных координат:
        tvbo: VBO = None

        # Буфер индексов:
        ibo: IBO = None

        # Буфер атрибутов:
        vao: VAO = None

        # Функция ручной инициализации:
        @staticmethod
        def _init_() -> None:
            # Создаём общие буферы:
            RenderPipeline.Sprite.vvbo = VBO(np.array(RenderPipeline.Sprite.vertices, dtype=np.float32), None)
            RenderPipeline.Sprite.tvbo = VBO(np.array(RenderPipeline.Sprite.texcoords, dtype=np.float32), None)
            RenderPipeline.Sprite.ibo = IBO(np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32), None)
            RenderPipeline.Sprite.vao = VAO()

            # Устанавливаем атрибуты vao:
            RenderPipeline.Sprite.vao.begin()   # Используем VAO.
            RenderPipeline.Sprite.ibo.begin()   # Используем IBO.
            RenderPipeline.Sprite.vvbo.begin()  # Используем VBO сетку.
            RenderPipeline.Sprite.vao.attrib_pointer(location=0, count=3)  # Вершина состоит из трёх чисел.
            RenderPipeline.Sprite.vvbo.end()    # Не используем VBO сетку.
            RenderPipeline.Sprite.tvbo.begin()  # Используем VBO текстурных координат.
            RenderPipeline.Sprite.vao.attrib_pointer(location=1, count=2)  # Координаты состоят из двух чисел.
            RenderPipeline.Sprite.tvbo.end()   # Не используем VBO текстурных координат.
            RenderPipeline.Sprite.vao.end()    # Не используем VAO.
            RenderPipeline.Sprite.ibo.end()    # Не используем IBO.

    # Инициализация конвейера рендеринга:
    @staticmethod
    def init() -> None:
        # Компилируем шейдер по умолчанию:
        RenderPipeline.default_shader.compile()

        # Инициализация скайбокса:
        RenderPipeline.Skybox.CubeMap._init_()

        # Инициализация простой отрисовки:
        RenderPipeline.SimpleDraw._init_()

        # Инициализация спрайта:
        RenderPipeline.Sprite._init_()

    # Удаление конвейера рендеринга:
    @staticmethod
    def destroy() -> None:
        # Удаляем шейдер по умолчанию:
        RenderPipeline.default_shader.destroy()

        # Удаляем всё из скайбокса:
        RenderPipeline.Skybox.CubeMap.vvbo.destroy()
        RenderPipeline.Skybox.CubeMap.tvbo.destroy()
        RenderPipeline.Skybox.CubeMap.vao.destroy()

        # Удаляем всё из отрисовки примитивов:
        RenderPipeline.SimpleDraw.vvbo.destroy()
        RenderPipeline.SimpleDraw.vao.destroy()

        # Удаляем всё из спрайта:
        RenderPipeline.Sprite.vvbo.destroy()
        RenderPipeline.Sprite.tvbo.destroy()
        RenderPipeline.Sprite.vao.destroy()


# Класс рендер-холста:
class RenderCanvas:
    def __init__(self, camera2d, width: int = None, height: int = None) -> None:
        from .sprite import Sprite2D

        if width is not None and height is not None:
            wdth, hght = int(width), int(height)
        elif camera2d is not None:
            wdth, hght = camera2d.width, camera2d.height

        self.camera      = camera2d
        self.texture     = Texture(size=(wdth, hght))
        self.framebuffer = FrameBuffer(self.texture)
        self.sprite      = Sprite2D(self.texture)
        self._old_size_  = self.camera.size
        self._is_begin_  = False

    # Проверить изменение размера камеры:
    def _check_size_(self) -> None:
        if self.camera.size != self._old_size_:
            self.resize(*self.camera.size.xy)
            self._old_size_ = self.camera.size

    # Начать рисовать на текстуре конвейера рендеринга:
    def begin(self) -> "RenderCanvas":
        if self._is_begin_:
            raise Exception(
                "Function \".end()\" was not called in the last iteration of the loop.\n"
                "The function \".begin()\" cannot be called, since the last one "
                "\".begin()\" was not closed by the \".end()\" function.")
        self._check_size_()  # Проверяем изменился ли размер камеры.
        self._is_begin_ = True
        self.framebuffer.begin()
        return self

    # Закончить рисовать на текстуре конвейера рендеринга:
    def end(self) -> "RenderCanvas":
        if self._is_begin_: self._is_begin_ = False
        else: raise Exception("The \".begin()\" function was not called before the \".end()\" function.")
        self.framebuffer.end()
        return self

    # Отрисовать текстурку конвейера рендеринга как спрайт, на весь экран:
    def render(self, flip_y: bool = True, custom_shader: bool = False) -> "RenderCanvas":
        if self._is_begin_:
            raise Exception(
                "You cannot call the \".render()\" function after \".begin()\" and not earlier than \".end()\""
            )

        self.camera.ui_begin()
        if flip_y: rect = vec4(0, self.texture.height, self.texture.width, -self.texture.height)
        else: rect = vec4(0, 0, self.texture.width, self.texture.height)
        self.sprite.render(*rect, custom_shader=custom_shader)
        self.camera.ui_end()
        return self

    # Очистить кадровый буфер:
    def clear(self, color: list = None) -> "RenderCanvas":
        self._check_size_()  # Проверяем изменился ли размер камеры.
        self.framebuffer.clear(color)
        return self

    # Изменить размер текстурки конвейера рендеринга:
    def resize(self, width: int, height: int) -> "RenderCanvas":
        # Останавливаем использование кадрового буфера:
        if self._is_begin_: self.end()

        self.framebuffer.resize(int(width), int(height))
        return self

    # Удалить конвейер рендеринга:
    def destroy(self) -> None:
        self.framebuffer.destroy()
        self.texture.destroy()
