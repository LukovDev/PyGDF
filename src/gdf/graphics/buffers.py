#
# buffers.py - Содержит классы буферов OpenGL.
#


# Импортируем:
import array
import ctypes
from .texture import Texture
from .gl import *
from ..math import numpy as np


# Класс для отслеживания количества отрисованных примитивов:
class GLQuery:
    def __init__(self) -> None:
        self.id = gl.glGenQueries(1)[0]

    # Начать отслеживание отрисовки:
    def begin(self) -> "GLQuery":
        gl.glBeginQuery(gl.GL_PRIMITIVES_GENERATED, self.id)
        return self

    # Закончить отслеживание отрисовки:
    def end(self) -> "GLQuery":
        gl.glEndQuery(gl.GL_PRIMITIVES_GENERATED)
        return self

    # Получить количество отрисованных примитивов:
    def get_primitives(self) -> int:
        return gl.glGetQueryObjectuiv(self.id, gl.GL_QUERY_RESULT)

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteQueries(1, [self.id])
        self.id = None


# Shader Storage Buffer Object:
class SSBO:
    def __init__(self, data: np.ndarray) -> None:
        self.id = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, self.id)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)

    # Использовать буфер:
    def begin(self, bind_base: int = 0) -> "SSBO":
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, int(bind_base), self.id)
        gl.glMemoryBarrier(gl.GL_SHADER_STORAGE_BARRIER_BIT)
        return self

    # Перестать использовать буфер:
    def end(self) -> "SSBO":
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 0, 0)
        return self

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteBuffers(1, [self.id])
        self.id = None


# Кадровый буфер:
class FrameBuffer:
    def __init__(self, texture: Texture) -> None:
        self.texture = texture
        self.id = gl.glGenFramebuffers(1)
        self._id_before_begin_ = gl.glGetIntegerv(gl.GL_FRAMEBUFFER_BINDING)
        self.attach_texture(self.texture.id, gl.GL_COLOR_ATTACHMENT0)

    # Привязать текстуру к фреймбуферу:
    def attach_texture(self, texture_id: int, attach_type: int = gl.GL_COLOR_ATTACHMENT0) -> "FrameBuffer":
        self.begin()
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, attach_type, gl.GL_TEXTURE_2D, texture_id, 0)
        self.end()
        return self

    # Использовать буфер:
    def begin(self) -> "FrameBuffer":
        self._id_before_begin_ = gl.glGetIntegerv(gl.GL_FRAMEBUFFER_BINDING)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)
        return self

    # Перестать использовать буфер:
    def end(self) -> "FrameBuffer":
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._id_before_begin_)
        return self

    # Очистить кадровый буфер:
    def clear(self, color: list = None) -> "FrameBuffer":
        if color is None: color = [0, 0, 0, 1]

        # Ограничиваем альфа-канал от 0 до 1:
        if len(color) > 3: color[3] = min(max(color[3], 0.0), 1.0)

        # Очищаем:
        self.begin()
        gl.glClearColor(*color if len(color) > 3 else (*color, 1.0))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        self.end()
    
        return self
    
    # Изменить размер текстуры кадрового буфера:
    def resize(self, width: int, height: int) -> "FrameBuffer":
        self.texture.width = int(width)
        self.texture.height = int(height)
        wdth, hght = self.texture.width, self.texture.height
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture.id)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA8, wdth, hght, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteFramebuffers(1, [self.id])
        self.id = None


# Создать вершинный буфер:
class VBO:
    def __init__(self, vertices: np.ndarray | list, mode: int = gl.GL_STATIC_DRAW) -> None:
        self.id       = gl.glGenBuffers(1)
        self.vertices = None

        # VBO:
        if not isinstance(vertices, np.ndarray):
            linear_list = vertices if type(vertices[0]) not in (tuple, list) else [i for s in vertices for i in s]
            self.vertices = array.array("f", linear_list).tobytes()
        else: self.vertices = vertices

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glBufferData(
            gl.GL_ARRAY_BUFFER,
            self.vertices.nbytes if isinstance(self.vertices, np.ndarray) else len(self.vertices),
            self.vertices, int(mode)
        )

    # Отрисовать буфер:
    def render(self,
               color:               list = None,
               draw_mode:           int  = gl.GL_TRIANGLES,
               poly_mode:           int  = gl.GL_FILL,
               triangle_vertices:   int  = 3,
               vertice_value_count: int  = 3,
               attributes:          list = None,
               accuracy:            int  = gl.GL_FLOAT) -> None:
        if color      is None: color = [1.0, 1.0, 1.0]
        if attributes is None: attributes = [(3, ctypes.c_float)]

        # Проверка правильности параметра accuracy:
        if accuracy not in (gl.GL_DOUBLE, gl.GL_FLOAT, gl.GL_INT):
            raise ValueError("Unsupported accuracy type. Use GL_FLOAT or GL_INT.")

        # Устанавливаем цвет заливки модели:
        gl.glColor(*color[:4])

        # Режим отображения:
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, poly_mode)

        # Настройка перед отрисовкой:
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        # Устанавливаем каждый атрибут:
        offset, stride = 0, sum(count for count, _ in attributes)
        for i, (count, attr_type) in enumerate(attributes):
            gl.glEnableVertexAttribArray(i)
            gl.glVertexAttribPointer(
                i, count, int(accuracy), gl.GL_FALSE,
                stride * ctypes.sizeof(attr_type),
                ctypes.c_void_p(offset))

            # Смещаем указатель на следующий атрибут:
            offset += count * ctypes.sizeof(attr_type)

        # Отрисовка:
        gl.glDrawArrays(draw_mode, 0, len(self.vertices) // triangle_vertices)

        # Возвращаем настройки отрисовки по умолчанию:
        for i in range(len(attributes)): gl.glDisableVertexAttribArray(i)
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        # Возвращаем обычный режим отрисовки:
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteBuffers(1, [self.id])
        self.id = None
