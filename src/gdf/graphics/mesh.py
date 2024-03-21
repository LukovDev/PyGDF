#
# mesh.py - Создаёт базовый меш.
#


# Импортируем:
if True:
    from .gl import *
    import numpy as np


# Класс базового меша:
class BaseMesh:
    def __init__(self) -> None:
        self.vertices = []
        self.normals = []
        self.indices = []
        self.vbo_vertices = None
        self.vbo_normals = None
        self.vbo_indices = None

    # Создать VBO:
    def create_vbo(self, data) -> int:
        vbo_id = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo_id)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        return vbo_id

    # Создать VBOs для вершин, нормалей и индексов:
    def create_vbos(self) -> None:
        self.vbo_vertices = self.create_vbo(np.array(self.vertices, dtype=np.float64))
        self.vbo_normals = self.create_vbo(np.array(self.normals, dtype=np.float64))
        self.vbo_indices = self.create_vbo(np.array(self.indices, dtype=np.uint32))

    # Отрисовка:
    def render(self) -> None:
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_vertices)
        gl.glVertexPointer(3, gl.GL_DOUBLE, 0, None)

        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_normals)
        gl.glNormalPointer(gl.GL_DOUBLE, 0, None)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.vbo_indices)
        gl.glDrawElements(gl.GL_TRIANGLES, len(self.indices), gl.GL_UNSIGNED_INT, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)

    # Отрисовка линий сетки:
    def render_grid(self, color: list = (1.0, 1.0, 1.0, 1.0), line_width: float = 1.0) -> None:
        gl.glLineWidth(line_width)
        gl.glDisable(gl.GL_LIGHTING)
        gl.glDisable(gl.GL_POINT_SMOOTH)
        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_vertices)
        gl.glVertexPointer(3, gl.GL_DOUBLE, 0, None)

        gl.glEnableClientState(gl.GL_NORMAL_ARRAY)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo_normals)
        gl.glNormalPointer(gl.GL_DOUBLE, 0, None)

        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.vbo_indices)
        gl.glDrawElements(gl.GL_LINES, len(self.indices), gl.GL_UNSIGNED_INT, None)

        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, 0)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_NORMAL_ARRAY)

    # Удаление сетки:
    def destroy(self, vbo_id: int = 0) -> None:
        gl.glDeleteBuffers(1, [self.vbo_vertices, self.vbo_normals, self.vbo_indices])
