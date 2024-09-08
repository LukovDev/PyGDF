#
# buffers.py - Содержит классы буферов OpenGL.
#


# Импортируем:
from .gl import *
from ..math import numpy as np


# Shader Storage Buffer Object:
class SSBO:
    def __init__(self, data: np.ndarray) -> None:
        self.id = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, self.id)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)

    # Использовать буфер:
    def begin(self) -> "SSBO":
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 0, self.id)
        gl.glMemoryBarrier(gl.GL_SHADER_STORAGE_BARRIER_BIT)
        return self

    # Перестать использовать буфер:
    def end(self) -> "SSBO":
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 0, 0)
        return self

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteBuffers(1, [self.id])


# Кадровый буфер:
class FrameBuffer:
    def __init__(self, texture_id: int) -> None:
        self.id = gl.glGenFramebuffers(1)
        self._id_before_begin_ = gl.glGetIntegerv(gl.GL_FRAMEBUFFER_BINDING)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, texture_id, 0)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self._id_before_begin_)

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

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteFramebuffers(1, [self.id])


# Создать вершинный буфер:
class VBO:
    def __init__(self, vertices: np.ndarray, mode: int = gl.GL_STATIC_DRAW) -> None:
        self.id       = gl.glGenBuffers(1)
        self.vertices = vertices

        # Vertex buffer:
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices, int(mode))

    # Отрисовать буфер:
    def render(self,
               color: list = None,
               draw_mode: int = gl.GL_TRIANGLES,
               poly_mode: int = gl.GL_FILL,
               triangle_vertices: int = 3,
               accuracy: int = gl.GL_FLOAT) -> None:
        if color is None: color = [1.0, 1.0, 1.0]

        # Проверка правильности параметра accuracy:
        if accuracy not in (gl.GL_DOUBLE, gl.GL_FLOAT, gl.GL_INT):
            raise ValueError("Unsupported accuracy type. Use GL_FLOAT or GL_INT.")

        # Устанавливаем цвет заливки модели:
        gl.glColor(*color[:4])

        # Режим отображения:
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, poly_mode)

        # Настройка перед отрисовкой:
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        gl.glVertexPointer(3, int(accuracy), 0, None)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)

        # Отрисовка:
        gl.glDrawArrays(draw_mode, 0, len(self.vertices) // triangle_vertices)

        # Возвращаем настройки отрисовки по умолчанию:
        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        # Возвращаем обычный режим отрисовки:
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteBuffers(1, [self.id])
