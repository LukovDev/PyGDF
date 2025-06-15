#
# draw.py - Создаёт класс функций для отрисовки примитивов чтобы не использовать вызовы OpenGL напрямую.
#


# Импортируем:
from .gl import *
from .render import RenderPipeline
from ..math import *
from ..math import numpy as np


# Класс простой отрисовки примитивов (НЕ РЕКОМЕНДУЕТСЯ РИСОВАТЬ БОЛЬШИЕ И СЛОЖНЫЕ ПРИМИТИВЫ!!!):
class SimpleDraw:
    max_verts: int = 0  # Максимальное количество вершин в буфере.

    # Функция отрисовки вершин:
    @staticmethod
    def _draw_(color: vec3|vec4, verts: np.ndarray, draw_mode: int = gl.GL_LINES, poly_mode: int = gl.GL_FILL) -> None:
        if color is None: color = vec4(1.0)
        if isinstance(color, (vec3, glm.vec3)): color = vec4(color, 1.0)
        vert_count = len(verts)

        # Начинаем использовать шейдер и буферы:
        RenderPipeline.default_shader.begin()
        RenderPipeline.SimpleDraw.vao.begin()
        RenderPipeline.SimpleDraw.vvbo.begin()

        # Используем шейдер спрайта для отрисовки примитива (без текстуры):
        if draw_mode == gl.GL_POINTS: RenderPipeline.default_shader.set_uniform("u_use_points", True)
        RenderPipeline.default_shader.set_uniform("u_use_texture", False)
        RenderPipeline.default_shader.set_uniform("u_color", color)
        RenderPipeline.default_shader.set_uniform("u_model", mat4(1.0))

        # Пересоздаём буфер, если число вершин больше текущего максимума:
        if vert_count > SimpleDraw.max_verts:
            SimpleDraw.max_verts = vert_count
            RenderPipeline.SimpleDraw.vvbo.set_data(verts, None, gl.GL_DYNAMIC_DRAW, use_begin_end=False)
        # Иначе просто обновляем данные в буфере:
        else: RenderPipeline.SimpleDraw.vvbo.set_subdata(verts, use_begin_end=False)

        # Рисуем вершины:
        RenderPipeline.SimpleDraw.vvbo.render(draw_mode, poly_mode, use_begin_end=False)

        # Перестаём использовать буферы и шейдер:
        if draw_mode == gl.GL_POINTS: RenderPipeline.default_shader.set_uniform("u_use_points", False)
        RenderPipeline.SimpleDraw.vvbo.end()
        RenderPipeline.SimpleDraw.vao.end()
        RenderPipeline.default_shader.end()

    # Нарисовать точку:
    @staticmethod
    def point(color: vec3|vec4, point: vec2|vec3, size: float = 1.0) -> None:
        if isinstance(point, (vec2, glm.vec2)): point = vec3(point.xy, 0.0)
        gl.glPointSize(size)
        SimpleDraw._draw_(color, np.array([point], dtype=np.float32), gl.GL_POINTS)

    # Нарисовать линию:
    @staticmethod
    def line(color: vec3|vec4, point1: vec2|vec3, point2: vec2|vec3, width: float = 1.0) -> None:
        if isinstance(point1, (vec2, glm.vec2)): point1 = vec3(point1.xy, 0.0)
        if isinstance(point2, (vec2, glm.vec2)): point2 = vec3(point2.xy, 0.0)
        gl.glLineWidth(width)
        SimpleDraw._draw_(color, np.array([point1, point2], dtype=np.float32), gl.GL_LINES)

    # Нарисовать ломаную линию:
    @staticmethod
    def line_strip(color: vec3|vec4, points: list, width: float = 1.0) -> None:
        gl.glLineWidth(width)
        SimpleDraw._draw_(color, np.array(points, dtype=np.float32), gl.GL_LINE_STRIP)

    # Нарисовать замкнутую ломаную линию:
    @staticmethod
    def line_loop(color: vec3|vec4, points: list, width: float = 1.0) -> None:
        gl.glLineWidth(width)
        SimpleDraw._draw_(color, np.array(points, dtype=np.float32), gl.GL_LINE_LOOP)

    # Нарисовать треугольники:
    @staticmethod
    def triangles(color: vec3|vec4, vertices: list) -> None:
        SimpleDraw._draw_(color, np.array(vertices, dtype=np.float32), gl.GL_TRIANGLES)

    # Нарисовать треугольники с общей стороной:
    @staticmethod
    def triangle_strip(color: vec3|vec4, vertices: list) -> None:
        SimpleDraw._draw_(color, np.array(vertices, dtype=np.float32), gl.GL_TRIANGLE_STRIP)

    # Нарисовать треугольники последняя вершина которой будет соединена с первой:
    @staticmethod
    def triangle_fan(color: vec3|vec4, vertices: list) -> None:
        SimpleDraw._draw_(color, np.array(vertices, dtype=np.float32), gl.GL_TRIANGLE_FAN)

    # Нарисовать квадрат:
    @staticmethod
    def square(color: vec3|vec4, point: vec2, size: vec2, width: float = 1.0) -> None:
        x, y, w, h = point.x, point.y, size.x, size.y
        SimpleDraw.line_loop(color, [(x, y, 0), (x+w, y, 0), (x+w, y+h, 0), (x, y+h, 0)], width)

    # Нарисовать квадрат с заливкой:
    @staticmethod
    def square_fill(color: vec3|vec4, point: vec2, size: vec2) -> None:
        x, y, w, h = point.x, point.y, size.x, size.y
        vertices = [(x, y, 0.0), (x+w, y, 0.0), (x+w, y+h, 0.0), (x+w, y+h, 0.0), (x, y+h, 0.0), (x, y, 0.0)]
        SimpleDraw.triangles(color, vertices)

    # Нарисовать круг:
    @staticmethod
    def circle(color: vec3|vec4, center: vec2, radius: float, width: float = 1.0, num_vertices: int = 24) -> None:
        if num_vertices < 3: num_vertices = 3
        vertices_list = []
        for index in range(num_vertices):
            rad_angle = radians((360.0/num_vertices)*index)
            vertices_list.append([center[0]+sin(rad_angle)*radius, center[1]+cos(rad_angle)*radius, 0.0])
        SimpleDraw.line_loop(color, vertices_list, width)

    # Нарисовать круг с заливкой:
    @staticmethod
    def circle_fill(color: vec3|vec4, center: vec2, radius: float, num_vertices: int = 24) -> None:
        if num_vertices < 3: num_vertices = 3
        angle_step = 2 * pi / num_vertices
        triangles = []
        for i in range(num_vertices):
            theta1, theta2 = i * angle_step, (i + 1) * angle_step
            triangles.extend([
                (center[0], center[1], 0.0),
                (center[0] + sin(theta1) * radius, center[1] + cos(theta1) * radius, 0.0),
                (center[0] + sin(theta2) * radius, center[1] + cos(theta2) * radius, 0.0)
            ])
        SimpleDraw.triangles(color, triangles)

    # Нарисовать звёздочку:
    @staticmethod
    def star(color: vec3|vec4, center: vec2, outradius: float, inradius: float,
             num_vertices: int = 5, width: float = 1.0) -> None:
        if num_vertices < 2: num_vertices = 2
        vertices_list = []
        for index in range(num_vertices*2):
            radius = outradius if not index % 2 else inradius
            rad_angle = radians(index*180.0/num_vertices)
            vertices_list.append([center[0]+sin(rad_angle)*radius, center[1]+cos(rad_angle)*radius, 0.0])
        SimpleDraw.line_loop(color, vertices_list, width)

    # Нарисовать звёздочку с заливкой:
    @staticmethod
    def star_fill(color: vec3|vec4, center: vec2, outradius: float, inradius: float, num_vertices: int = 5) -> None:
        if num_vertices < 2: num_vertices = 2
        triangles = []
        for i in range(num_vertices * 2):
            r1 = outradius if i % 2 == 0 else inradius
            r2 = outradius if (i+1) % 2 == 0 else inradius
            a1 = radians(i * 180.0 / num_vertices)
            a2 = radians((i+1) * 180.0 / num_vertices)
            triangles.extend([
                (center.x, center.y, 0.0),
                (center.x + sin(a1)*r1, center.y + cos(a1)*r1, 0.0),
                (center.x + sin(a2)*r2, center.y + cos(a2)*r2, 0.0),
            ])
        SimpleDraw.triangles(color, triangles)
