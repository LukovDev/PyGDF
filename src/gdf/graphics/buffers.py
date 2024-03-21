#
# buffers.py - Содержит классы буферов OpenGL.
#


# Импортируем:
if True:
    import numpy as np
    from .gl import *


# Shader Storage Buffer Object:
class SSBO:
    def __init__(self, data: np.ndarray) -> None:
        self.id = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, self.id)
        gl.glBufferData(gl.GL_SHADER_STORAGE_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)
        gl.glBindBuffer(gl.GL_SHADER_STORAGE_BUFFER, 0)

    # Использовать буфер:
    def begin(self) -> None:
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 0, self.id)
        gl.glMemoryBarrier(gl.GL_SHADER_STORAGE_BARRIER_BIT)

    # Перестать использовать буфер:
    def end(self) -> None:
        gl.glBindBufferBase(gl.GL_SHADER_STORAGE_BUFFER, 0, 0)

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteBuffers(1, [self.id])


# Фреймбуфер:
class FrameBuffer:
    def __init__(self, texture_id: int) -> None:
        self.id = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, texture_id, 0)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    # Использовать буфер:
    def begin(self) -> None:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.id)

    # Перестать использовать буфер:
    def end(self) -> None:
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    # Удалить буфер:
    def destroy(self) -> None:
        gl.glDeleteFramebuffers(1, [self.id])
