#
# r2d_verts_c.pyx - Код для создания мега оптимизированной быстрой функции поворота вершин 2D спрайта.
#
# Этот код никак не используется ядром, пока не будет скомпилирован.
#
# Это код на Cython. Создаёт файл динамического импорта модуля после компиляции.
# Этот код нужен чтобы не использовать тяжёлый numba, который увеличивает скорость запуска и размер сборки на ~+30-35мб.
# Но при этом, код ниже даже быстрее, чем если использовать numba @njit.
#


# Импортируем:
from libc.math cimport sin, cos, pi


# Сверхбыстрая функция для поворота четырёх 2D вершин (для 2D прямоугольника), вокруг их общего центра:
def _rot2d_vertices_rectangle_(float x, float y, int width, int height, float angle) -> list:
    # Подготовка значений:
    cdef float center_x      =  x + (width  / 2.0)
    cdef float center_y      =  y + (height / 2.0)
    cdef float angle_rad     = -(angle * (pi / 180.0))
    cdef float angle_rad_sin =  sin(angle_rad)
    cdef float angle_rad_cos =  cos(angle_rad)

    # Предварительные смещения:
    cdef float dx1 = x - center_x
    cdef float dy1 = y - center_y
    cdef float dx2 = x + width  - center_x
    cdef float dy2 = y - center_y
    cdef float dx3 = x + width  - center_x
    cdef float dy3 = y + height - center_y
    cdef float dx4 = x - center_x
    cdef float dy4 = y + height - center_y

    # Вычисление координат вершин:
    cdef float x1 = dx1 * angle_rad_cos - dy1 * angle_rad_sin + center_x
    cdef float y1 = dx1 * angle_rad_sin + dy1 * angle_rad_cos + center_y
    cdef float x2 = dx2 * angle_rad_cos - dy2 * angle_rad_sin + center_x
    cdef float y2 = dx2 * angle_rad_sin + dy2 * angle_rad_cos + center_y
    cdef float x3 = dx3 * angle_rad_cos - dy3 * angle_rad_sin + center_x
    cdef float y3 = dx3 * angle_rad_sin + dy3 * angle_rad_cos + center_y
    cdef float x4 = dx4 * angle_rad_cos - dy4 * angle_rad_sin + center_x
    cdef float y4 = dx4 * angle_rad_sin + dy4 * angle_rad_cos + center_y

    # Возвращаем 4 вершины спрайта:
    return [x1, y1, x2, y2, x3, y3, x4, y4]
