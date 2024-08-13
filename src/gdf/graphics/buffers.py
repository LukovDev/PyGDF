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
