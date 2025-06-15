#
# buffers.py - Содержит классы буферов OpenGL.
#


# Импортируем:
import ctypes
from .gl import *
from .texture import Texture
from . import BufferManager
from ..math import numpy as np


# Класс для отслеживания количества отрисованных примитивов:
class GLQuery:
    def __init__(self) -> None:
        self.id = gl.glGenQueries(1)[0]

    # Начать отслеживание отрисовки:
    def begin(self) -> "GLQuery":
        if self.id is None: return self
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
        if self.id is not None:
            BufferManager.add(BufferManager.TYPE_QUERY_BUFFER, self.id)
            self.id = None


# Shader Storage Buffer Object (доступно начиная с OpenGL 4.3):
class SSBO:
    def __init__(self, data: np.ndarray) -> None:
        self.id = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, self.id)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)

    # Использовать буфер:
    def begin(self, bind_base: int = 0) -> "SSBO":
        if self.id is None: return self
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, int(bind_base), self.id)
        gl.glMemoryBarrier(gl.GL_SHADER_STORAGE_BARRIER_BIT)
        return self

    # Перестать использовать буфер:
    def end(self) -> "SSBO":
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 0, 0)
        return self

    # Удалить буфер:
    def destroy(self) -> None:
        if self.id is not None:
            BufferManager.add(BufferManager.TYPE_SHADER_STORAGE_BUFFER, self.id)
            self.id = None


# Кадровый буфер:
class FrameBuffer:
    def __init__(self, texture: Texture) -> None:
        self.texture = texture
        self.id = gl.glGenFramebuffers(1)
        self.attach_texture(self.texture, gl.GL_COLOR_ATTACHMENT0)

    # Использовать буфер:
    def begin(self) -> "FrameBuffer":
        if self.id is None: return self
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)
        return self

    # Перестать использовать буфер:
    def end(self) -> "FrameBuffer":
        if self.id is None: return self
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
        return self

    # Привязать текстуру к фреймбуферу:
    def attach_texture(self, texture: Texture, attach_type: int = gl.GL_COLOR_ATTACHMENT0,
                       use_begin_end: bool = True) -> "FrameBuffer":
        if self.id is None: return self
        if use_begin_end: self.begin()
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, attach_type, gl.GL_TEXTURE_2D, texture.id, 0)
        if use_begin_end: self.end()
        self.texture = texture
        return self

    # Очистить кадровый буфер:
    def clear(self, color: list = None, use_begin_end: bool = True) -> "FrameBuffer":
        if color is None: color = [0, 0, 0, 1]

        # Ограничиваем альфа-канал от 0 до 1:
        if len(color) > 3: color[3] = min(max(color[3], 0.0), 1.0)

        # Очищаем:
        if use_begin_end: self.begin()
        gl.glClearColor(*color if len(color) > 3 else (*color, 1.0))
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        if use_begin_end: self.end()
        return self

    # Изменить размер текстуры кадрового буфера:
    def resize(self, width: int, height: int) -> "FrameBuffer":
        self.texture.set_data(int(width), int(height), None, gl.GL_RGBA8, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE)
        return self

    # Удалить буфер:
    def destroy(self) -> None:
        if self.id is not None:
            BufferManager.add(BufferManager.TYPE_FRAME_BUFFER, self.id)
            self.id = None


# Класс буфера вершин:
class VBO:
    def __init__(self, data: np.ndarray, size: int = None, mode: int = gl.GL_STATIC_DRAW) -> None:
        self.id   = gl.glGenBuffers(1)
        self.data = data
        self.set_data(data, size, mode, True)

    # Использовать буфер:
    def begin(self) -> "VBO":
        if self.id is None: return self
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.id)
        return self

    # Перестать использовать буфер:
    def end(self) -> "VBO":
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        return self

    # Установить данные буфера (выделяет новую память и заново всё сохраняет):
    def set_data(self, data: np.ndarray, size: int = None,
                 mode: int = gl.GL_STATIC_DRAW, use_begin_end: bool = True) -> "VBO":
        self.data = data
        size = (0 if self.data is None else self.data.nbytes) if size is None else int(size)
        if use_begin_end: self.begin()
        gl.glBufferData(gl.GL_ARRAY_BUFFER, size, self.data, int(mode))
        if use_begin_end: self.end()
        return self

    # Изменить данные буфера (не выделяет новую память а просто изменяет данные):
    def set_subdata(self, data: np.ndarray, offset: int = 0, size: int = None, use_begin_end: bool = True) -> "VBO":
        self.data = data
        size = (0 if self.data is None else self.data.nbytes) if size is None else int(size)
        if use_begin_end: self.begin()
        gl.glBufferSubData(gl.GL_ARRAY_BUFFER, offset, size, self.data)
        if use_begin_end: self.end()
        return self

    # Получить размер буфера:
    def get_size(self, use_begin_end: bool = True) -> int:
        if use_begin_end: self.begin()
        size = int(gl.glGetBufferParameteriv(gl.GL_ARRAY_BUFFER, gl.GL_BUFFER_SIZE))
        if use_begin_end: self.end()
        return size

    # Отрисовать буфер:
    def render(self, draw_mode: int = gl.GL_TRIANGLES, poly_mode: int = gl.GL_FILL,
               first: int = 0, count: int = None, use_begin_end: bool = True) -> "VBO":
        """ draw_mode:
            GL_POINTS         – Точки.
            GL_LINE_STRIP     – Ломаная линия, соединяющая последовательные вершины.
            GL_LINE_LOOP      – Ломаная линия, замкнутая в цикл.
            GL_LINES          – Отдельные линии, каждая пара вершин образует линию.
            GL_TRIANGLE_STRIP – Треугольная полоса, где каждая новая вершина вместе с предыдущими образует треугольник.
            GL_TRIANGLE_FAN   – Треугольная веерная отрисовка.
            GL_TRIANGLES      – Треугольники, каждые три вершины образуют треугольник.
        """
        if self.id is None: return self
        if use_begin_end: self.begin()
        if poly_mode != gl.GL_FILL: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, poly_mode)
        gl.glDrawArrays(draw_mode, first, len(self.data) if count is None else count)
        if poly_mode != gl.GL_FILL: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        if use_begin_end: self.end()
        return self

    # Отрисовать буфер учитывая IBO:
    def render_elements(self, draw_mode: int = gl.GL_TRIANGLES, poly_mode: int = gl.GL_FILL, offset: int = None,
                        count: int = None, data_type: int = gl.GL_UNSIGNED_INT, use_begin_end: bool = True) -> "VBO":
        offset = ctypes.c_void_p(0 if offset is None else offset)
        data_type = gl.GL_UNSIGNED_INT if data_type is None else data_type
        if self.id is None: return self
        if use_begin_end: self.begin()
        if poly_mode != gl.GL_FILL: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, poly_mode)
        gl.glDrawElements(draw_mode, 6 if count is None else count, data_type, offset)
        if poly_mode != gl.GL_FILL: gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        if use_begin_end: self.end()
        return self

    # Удалить буфер:
    def destroy(self) -> None:
        if self.id is not None:
            BufferManager.add(BufferManager.TYPE_VERTEX_BUFFER, self.id)
            self.id = None


# Класс буфера индексов вершин:
class IBO:
    def __init__(self, data: np.ndarray, size: int = None, mode: int = gl.GL_STATIC_DRAW) -> None:
        self.id   = gl.glGenBuffers(1)
        self.data = data
        self.set_data(data, size, mode, True)

    # Использовать индексный буфер:
    def begin(self) -> "IBO":
        if self.id is None: return self
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.id)
        return self

    # Перестать использовать индексный буфер:
    def end(self) -> "IBO":
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)
        return self

    # Установить данные буфера:
    def set_data(self, data: np.ndarray, size: int = None,
                 mode: int = gl.GL_STATIC_DRAW, use_begin_end: bool = True) -> "IBO":
        self.data = data
        size = (0 if self.data is None else self.data.nbytes) if size is None else int(size)
        if use_begin_end: self.begin()
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, size, self.data, int(mode))
        if use_begin_end: self.end()
        return self

    # Обновить подмножество данных:
    def set_subdata(self, data: np.ndarray, offset: int = 0, size: int = None, use_begin_end: bool = True) -> "IBO":
        self.data = data
        size = (0 if self.data is None else self.data.nbytes) if size is None else int(size)
        if use_begin_end: self.begin()
        gl.glBufferSubData(gl.GL_ELEMENT_ARRAY_BUFFER, offset, size, self.data)
        if use_begin_end: self.end()
        return self

    # Получить размер буфера:
    def get_size(self, use_begin_end: bool = True) -> int:
        if use_begin_end: self.begin()
        size = int(gl.glGetBufferParameteriv(gl.GL_ELEMENT_ARRAY_BUFFER, gl.GL_BUFFER_SIZE))
        if use_begin_end: self.end()
        return size

    # Удалить буфер:
    def destroy(self) -> None:
        if self.id is not None:
            BufferManager.add(BufferManager.TYPE_INDEX_BUFFER, self.id)
            self.id = None


# Класс буфера вершинных атрибутов:
class VAO:
    def __init__(self) -> None:
        self.id = gl.glGenVertexArrays(1)

    # Использовать буфер:
    def begin(self) -> "VAO":
        if self.id is None: return self
        gl.glBindVertexArray(self.id)
        return self

    # Перестать использовать буфер:
    def end(self) -> "VAO":
        gl.glBindVertexArray(0)
        return self

    # Установить атрибуты вершин:
    def attrib_pointer(self, location: int, count: int, data_type: int = gl.GL_FLOAT,
                       normalize: bool = False, stride: int = 0, offset: int = None) -> "VAO":
        offset = ctypes.c_void_p(0 if offset is None else offset)
        gl.glVertexAttribPointer(location, count, data_type, normalize, stride, offset)
        gl.glEnableVertexAttribArray(location)
        return self

    # Удалить буфер:
    def destroy(self) -> None:
        if self.id is not None:
            BufferManager.add(BufferManager.TYPE_VERTEX_ARRAY_BUFFER, self.id)
            self.id = None
