#
# draw.py - Создаёт класс функций для отрисовки примитивов чтобы не использовать вызовы OpenGL напрямую.
#


# Импортируем:
if True:
    from .gl import *
    from ..math import *


# Класс отрисовки примитивов:
class Draw2D:
    # Нарисовать точку:
    @staticmethod
    def point(color: list, point: tuple, size: float) -> None:
        if not color: color = [1, 1, 1]
        gl.glPointSize(size)
        gl.glColor(*color)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex2d(*point)
        gl.glEnd()

    # Нарисовать линию:
    @staticmethod
    def line(color: list, point1: tuple, point2: tuple, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        if smooth: gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(width)
        gl.glColor(*color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2d(*point1)
        gl.glVertex2d(*point2)
        gl.glEnd()
        if smooth: gl.glDisable(gl.GL_LINE_SMOOTH)

    # Нарисовать ломаную линию:
    @staticmethod
    def line_strip(color: list, points: list, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        if smooth: gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(width)
        gl.glColor(*color)
        gl.glBegin(gl.GL_LINE_STRIP)
        for p in points: gl.glVertex2d(*p)
        gl.glEnd()
        if smooth: gl.glDisable(gl.GL_LINE_SMOOTH)

    # Нарисовать замкнутую ломаную линию:
    @staticmethod
    def line_loop(color: list, points: list, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        if smooth: gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(width)
        gl.glColor(*color)
        gl.glBegin(gl.GL_LINE_LOOP)
        for p in points: gl.glVertex2d(*p)
        gl.glEnd()
        if smooth: gl.glDisable(gl.GL_LINE_SMOOTH)

    # Нарисовать треугольники:
    @staticmethod
    def triangles(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLES)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать треугольники с общей стороной:
    @staticmethod
    def triangle_strip(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать треугольники последняя вершина которой будет соединена с первой:
    @staticmethod
    def triangle_loop(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать квадрат из каждых 4-х вершин:
    @staticmethod
    def quads(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_QUADS)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать квадрат из каждых 4-х вершин с общей стороной:
    @staticmethod
    def quads_strip(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_QUAD_STRIP)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать многоугольник (тоже самое как line_loop но с заливкой):
    @staticmethod
    def polygon(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_POLYGON)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать круг:
    @staticmethod
    def circle(color: list, point: tuple, radius: float, width: float = 1,
               smooth: bool = False, num_vertices: int = 32) -> None:
        if not color: color = [1, 1, 1]
        if num_vertices < 3: num_vertices = 3
        vertices_list = []
        for index in range(num_vertices):
            rad_angle = radians((360/num_vertices)*index)
            vertices_list.append([sin(rad_angle)*radius, cos(rad_angle)*radius])
        Draw2D.line_loop(color, vertices_list, width, smooth)

    # Нарисовать круг с заливкой:
    @staticmethod
    def circle_fill(color: list, point: tuple, radius: float, num_vertices: int = 32) -> None:
        if not color: color = [1, 1, 1]
        if num_vertices < 3: num_vertices = 3
        vertices_list = []
        for index in range(num_vertices):
            rad_angle = radians((360/num_vertices)*index)
            vertices_list.append([sin(rad_angle)*radius, cos(rad_angle)*radius])
        Draw2D.polygon(color, vertices_list)
