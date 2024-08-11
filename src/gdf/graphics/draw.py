#
# draw.py - Создаёт класс функций для отрисовки примитивов чтобы не использовать вызовы OpenGL напрямую.
#


# Импортируем:
from .gl import *
from ..math import *


# Класс отрисовки 2D примитивов:
class Draw2D:
    # Нарисовать точку:
    @staticmethod
    def point(color: list, point: tuple, size: float) -> None:
        if not color: color = [1, 1, 1]
        gl.glPointSize(size)
        gl.glColor(*color)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex(*point)
        gl.glEnd()

    # Нарисовать линию:
    @staticmethod
    def line(color: list, point1: tuple, point2: tuple, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        if smooth: gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(width)
        gl.glColor(*color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex(*point1)
        gl.glVertex(*point2)
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
        for p in points: gl.glVertex(*p)
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
        for p in points: gl.glVertex(*p)
        gl.glEnd()
        if smooth: gl.glDisable(gl.GL_LINE_SMOOTH)

    # Нарисовать треугольники:
    @staticmethod
    def triangles(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLES)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать треугольники с общей стороной:
    @staticmethod
    def triangle_strip(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать треугольники последняя вершина которой будет соединена с первой:
    @staticmethod
    def triangle_fan(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать квадрат из каждых 4-х вершин:
    @staticmethod
    def quads(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_QUADS)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать квадрат из каждых 4-х вершин с общей стороной:
    @staticmethod
    def quads_strip(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_QUAD_STRIP)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать многоугольник:
    @staticmethod
    def polygon(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_POLYGON)
        for v in vertices: gl.glVertex2d(*v)
        gl.glEnd()

    # Нарисовать квадрат:
    @staticmethod
    def square(color: list, point: tuple, size: tuple, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        x, y, w, h = point[0], point[1], size[0], size[1]
        Draw2D.line_loop(color, [(x, y), (x+w, y), (x+w, y+h), (x, y+h)], width, smooth)

    # Нарисовать квадрат с заливкой:
    @staticmethod
    def square_fill(color: list, point: tuple, size: tuple) -> None:
        if not color: color = [1, 1, 1]
        x, y, w, h = point[0], point[1], size[0], size[1]
        Draw2D.quads(color, [(x, y), (x+w, y), (x+w, y+h), (x, y+h)])

    # Нарисовать круг:
    @staticmethod
    def circle(color: list, center: tuple, radius: float, width: float = 1,
               smooth: bool = False, num_vertices: int = None) -> None:
        if not color: color = [1, 1, 1]
        if num_vertices is None: num_vertices = int(pi*2*radius)//180
        if num_vertices < 3: num_vertices = 3
        vertices_list = []
        for index in range(num_vertices):
            rad_angle = radians((360/num_vertices)*index)
            vertices_list.append([center[0]+sin(rad_angle)*radius, center[1]+cos(rad_angle)*radius])
        Draw2D.line_loop(color, vertices_list, width, smooth)

    # Нарисовать круг с заливкой:
    @staticmethod
    def circle_fill(color: list, center: tuple, radius: float, num_vertices: int = 24) -> None:
        if not color: color = [1, 1, 1]
        if num_vertices < 3: num_vertices = 3
        vertices_list = []
        for index in range(num_vertices):
            rad_angle = radians((360/num_vertices)*index)
            vertices_list.append([center[0]+sin(rad_angle)*radius, center[1]+cos(rad_angle)*radius])
        Draw2D.polygon(color, vertices_list)

    # Нарисовать звёздочку:
    @staticmethod
    def star(color: list, center: tuple, outradius: float, inradius: float,
             num_vertices: int = 5, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        if num_vertices < 2: num_vertices = 2
        vertices_list = []
        for index in range(num_vertices*2):
            radius = outradius if not index % 2 else inradius
            rad_angle = radians(index*180/num_vertices)
            vertices_list.append([center[0]+sin(rad_angle)*radius, center[1]+cos(rad_angle)*radius])
        Draw2D.line_loop(color, vertices_list, width, smooth)

    # Нарисовать звёздочку с заливкой:
    @staticmethod
    def star_fill(color: list, center: tuple, outradius: float, inradius: float, num_vertices: int = 5) -> None:
        if not color: color = [1, 1, 1]
        if num_vertices < 2: num_vertices = 2
        vertices_list = []
        for index in range(num_vertices*2+1):
            radius = outradius if not index % 2 else inradius
            rad_angle = radians(index*180/num_vertices)
            vertices_list.append([center[0]+sin(rad_angle)*radius, center[1]+cos(rad_angle)*radius])
            vertices_list.append(list(center))
        Draw2D.triangle_strip(color, vertices_list)


# Класс отрисовки 3D примитивов:
class Draw3D:
    # Нарисовать точку:
    @staticmethod
    def point(color: list, point: list, size: float) -> None:
        if not color: color = [1, 1, 1]
        gl.glPointSize(size)
        gl.glColor(*color)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex(*point)
        gl.glEnd()

    # Нарисовать линию:
    @staticmethod
    def line(color: list, point1: list, point2: list, width: float = 1, smooth: bool = False) -> None:
        if not color: color = [1, 1, 1]
        if smooth: gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glLineWidth(width)
        gl.glColor(*color)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex(*point1)
        gl.glVertex(*point2)
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
        for p in points: gl.glVertex(*p)
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
        for p in points: gl.glVertex(*p)
        gl.glEnd()
        if smooth: gl.glDisable(gl.GL_LINE_SMOOTH)

    # Нарисовать треугольники:
    @staticmethod
    def triangles(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLES)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать треугольники с общей стороной:
    @staticmethod
    def triangle_strip(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLE_STRIP)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать треугольники последняя вершина которой будет соединена с первой:
    @staticmethod
    def triangle_fan(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_TRIANGLE_FAN)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать квадрат из каждых 4-х вершин:
    @staticmethod
    def quads(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_QUADS)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать квадрат из каждых 4-х вершин с общей стороной:
    @staticmethod
    def quads_strip(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_QUAD_STRIP)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()

    # Нарисовать многоугольник:
    @staticmethod
    def polygon(color: list, vertices: list) -> None:
        if not color: color = [1, 1, 1]
        gl.glColor(*color)
        gl.glBegin(gl.GL_POLYGON)
        for v in vertices: gl.glVertex(*v)
        gl.glEnd()
