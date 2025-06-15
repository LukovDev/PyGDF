#
# graphics_utils.pyx - Код для создания очень быстрых функций (на уровне языка си) для работы с графикой.
#
# Этот код никак не используется ядром, пока не будет скомпилирован.
#
# Это код на Cython. Создаёт файл динамического импорта модуля после компиляции.
# Этот код нужен чтобы не использовать тяжёлый numba, который увеличивает скорость запуска и размер сборки на ~+30-35мб.
# Но при этом, код ниже даже быстрее, чем если использовать numba @njit (по крайней мере в моих тестах).
#


# Импортируем:
cimport cython
import numpy as np
cimport numpy as np
from OpenGL import GL as gl
from libc.math cimport sin, cos, pi
from cpython.object cimport PyObject
from cpython.dict cimport PyDict_Next
from cpython.long cimport PyLong_Check, PyLong_AsLong


# Сверхбыстрая функция для поворота четырёх 2D вершин (для 2D прямоугольника), вокруг их общего центра:
cpdef list _rot2d_vertices_rectangle_(float x, float y, float width, float height, float angle):
    # Подготовка значений:
    cdef float center_x      = x + (width  / 2.0)
    cdef float center_y      = y + (height / 2.0)
    cdef float angle_rad     = -(angle * (pi / 180.0))
    cdef float angle_rad_sin = sin(angle_rad)
    cdef float angle_rad_cos = cos(angle_rad)

    # Предварительные смещения:
    cdef float dx1 = x - center_x
    cdef float dy1 = y - center_y
    cdef float dx2 = x + width  - center_x
    cdef float dy2 = y - center_y
    cdef float dx3 = x + width  - center_x
    cdef float dy3 = y + height - center_y
    cdef float dx4 = x - center_x
    cdef float dy4 = y + height - center_y

    # Возвращаем 4 вершины спрайта:
    return [
        dx1 * angle_rad_cos - dy1 * angle_rad_sin + center_x,
        dx1 * angle_rad_sin + dy1 * angle_rad_cos + center_y,
        dx2 * angle_rad_cos - dy2 * angle_rad_sin + center_x,
        dx2 * angle_rad_sin + dy2 * angle_rad_cos + center_y,
        dx3 * angle_rad_cos - dy3 * angle_rad_sin + center_x,
        dx3 * angle_rad_sin + dy3 * angle_rad_cos + center_y,
        dx4 * angle_rad_cos - dy4 * angle_rad_sin + center_x,
        dx4 * angle_rad_sin + dy4 * angle_rad_cos + center_y,
    ]


# Функция для конвертации массива квадратов в массив треугольников:
cpdef list _convert_quads_to_triangles_(list vertices):
    cdef list new_vertices = []
    cdef int i

    for i in range(0, len(vertices), 8):
        new_vertices += [
            vertices[i+0], vertices[i+1],  # Нижний левый угол.
            vertices[i+2], vertices[i+3],  # Нижний правый угол.
            vertices[i+4], vertices[i+5],  # Верхний правый угол.
            vertices[i+4], vertices[i+5],  # Верхний правый угол.
            vertices[i+6], vertices[i+7],  # Верхный левый угол.
            vertices[i+0], vertices[i+1],  # Нижний левый угол.
        ]

    return new_vertices


# Добавление спрайта в пакет текстур для пакетной отрисовки:
cpdef _sprite_batch_draw_(dict tb, dict tvc, list texcoord, object s, float x, float y, float w, float h, float a):
    cdef list vertices
    cdef int tid

    if PyLong_Check(s): tid = s
    else: tid = s.id

    # Вращаем вершины спрайта:
    if a != 0.0:
        vertices = _rot2d_vertices_rectangle_(x, y, w, h, a)
    else:
        vertices = [
            x    , y    ,  # Нижний левый угол.
            x + w, y    ,  # Нижний правый угол.
            x + w, y + h,  # Верхний правый угол.
            x    , y + h,  # Верхный левый угол.
        ]

    # Преобразовываем вершины + добавляем текстурные координаты:
    vertices = [
        vertices[0], vertices[1], 0.0, texcoord[0], texcoord[3],  # Нижний левый угол.
        vertices[2], vertices[3], 0.0, texcoord[2], texcoord[3],  # Нижний правый угол.
        vertices[4], vertices[5], 0.0, texcoord[2], texcoord[1],  # Верхний правый угол.
        vertices[6], vertices[7], 0.0, texcoord[0], texcoord[1],  # Верхный левый угол.
    ]

    # Если текстурки нет в уникальных текстурках:
    if tid not in tb: tb[tid] = []
    if tid not in tvc: tvc[tid] = 0

    # Добавляем новые вершины в сетку для конкретной текстуры:
    tb[tid] += vertices

    # Увеличиваем кол-во вершин для конкретной текстуры:
    tvc[tid] += 4  # Добавляем 6 вершин которые мы получили после преобразования.


# Отрисовка пакетов спрайтов:
cpdef _sprite_batch_render_(dict texbatches, dict texvcount, object set_sampler, object set_subdata, object vbo_render):
    cdef int key, count
    cdef list vertices

    for key, vertices in texbatches.items():
        # Получаем кол-во элементов из массива:
        count = texvcount.get(key, 0)

        set_sampler(PyLong_AsLong(key))  # Указываем id текстуры.
        set_subdata(np.array(vertices, dtype=np.float32).data, 0, count*5*4)
        vbo_render()
