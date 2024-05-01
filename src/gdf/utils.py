#
# utils.py - Содержит базовые полезные функции.
#


# Импортируем:
if True:
    from .graphics.camera import Camera2D
    from .math import *


# Найти угол наклона из двух координат:
def get_angle_points_2d(point1: tuple, point2: tuple) -> float:
    """ Возвращает угол между первой и второй координатой """

    return -degrees(atan2(point2[1]-point1[1], point2[0]-point1[0]))


# Найти точку из угла и радиуса:
def get_pos_angle_2d(angle: float, radius: float) -> tuple:
    """ Возвращает координаты в заданном радиусе и угле """

    return sin(radians(angle))*radius, cos(radians(angle))*radius


# Получить дельту для перемещения вектора в сторону угла на расстояние:
def get_delta_pos_angle_2d(angle: float, distance: float) -> tuple:
    """ Возвращает 2 числа для перемещения вектора в сторону угла """

    return (distance*sin(radians(angle)), distance*cos(radians(angle)))


# Получить дельту для перемещения вектора в сторону вектора на расстояние:
def get_delta_pos_vector_2d(vector: float, distance: float) -> tuple:
    """ Возвращает 2 числа для перемещения вектора в сторону вектора """

    return get_delta_pos_angle_2d(get_angle_points_2d((0, 0), normalize(vector)), distance)


# Получить вектор направления из угла:
def get_angle_to_direction_2d(angle: float) -> tuple:
    """ Возвращает 2 числа в виде направления из угла """

    return (-sin(radians(angle-90)), -cos(radians(angle-90)))


# Получить расстояние между двумя точками:
def get_distance_2d(point1: tuple, point2: tuple) -> float:
    """ Возвращает float дистанцию между двумя точками """

    return sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)


# Получить плавное перемещение:
def get_interpolation_2d(point1: tuple, point2: tuple, friction: float, delta_time: float) -> tuple:
    """ Возвращает 2 значения, которые представляют из себя расстояние между объектами, которое было уменьшено. """

    return ((point2[0]-point1[0])*1-friction)*(delta_time*60), ((point2[1]-point1[1])*(1-friction))*(delta_time*60)


# Получить точку в мировом пространстве при помощи луча:
def get_world_space_ray_3d(position: vec3, matproj, matview, screen_size: tuple, point: tuple, length: float) -> vec3:
    """ Принимает позицию камеры, матрицу проекции, матрицу вида, размер окна, точку из экрана и длину луча. """

    inv_matproj, inv_matview, position = numpy.linalg.inv(matproj), numpy.linalg.inv(matview), numpy.array(position.xyz)
    re = numpy.dot([2*point[0]/screen_size[0]-1, 1-2*point[1]/screen_size[1], -1, 1], inv_matproj)
    re[2], re[3] = -1, 0 ; rd = numpy.dot(re, inv_matview)[:3]/numpy.linalg.norm(numpy.dot(re, inv_matview)[:3])
    return vec3(position+rd*length)


# Получить список однотипных элементов списка:
def get_only_type_list(list: list, type: any) -> list:
    """ Возвращает список в котором только те типы, которые нам нужны. """

    return [i for i in list if isinstance(i, type)]


# Получить позицию точки из окна в мировом пространстве:
def screen_to_world_2d(camera: Camera2D, point_pos: tuple) -> tuple:
    # Позиция нижнего левого угла камеры с учётом метра и зума камеры:
    camera_posx = camera.position.x - ((camera.width  * camera.zoom) / 2) * (camera.meter / 100)
    camera_posy = camera.position.y - ((camera.height * camera.zoom) / 2) * (camera.meter / 100)

    # Позиция точки с учётом метра и зума камеры (Y координату точки инвертируем):
    point_posx = (point_pos[0]                * (camera.meter / 100)) * camera.zoom
    point_posy = (-(point_pos[1]-camera.height) * (camera.meter / 100)) * camera.zoom

    # Складываем и возвращаем результат:
    return camera_posx + point_posx, camera_posy + point_posy


# Функция для проверки пересечения круга с повёрнутым прямоугольником:
def is_circle_rot_rectangle_2d(center: tuple, radius: float, rect: list, angle: float) -> bool:
    """ Возвращает логическое значение при пересечении круга с повёрнутым прямоугольником """

    rdx = center[0]-(rect[0]+rect[2]/2)*cos(radians(angle))-(center[1]-(rect[1]+rect[3]/2))*sin(radians(angle))
    rdy = center[0]-(rect[0]+rect[2]/2)*sin(radians(angle))+(center[1]-(rect[1]+rect[3]/2))*cos(radians(angle))
    c = max(rect[0], min(rect[0]+rect[2], rect[0]+rdx)), max(rect[1], min(rect[1]+rect[3], rect[1]+rdy))
    return sqrt((rdx - (c[0] - rect[0]))**2 + (rdy - (c[1] - rect[1]))**2) <= radius


# Проверяем пересекается ли окружность с прямоугольником:
def is_circle_rectangle_2d(center: tuple, radius: float, rectangle: tuple) -> bool:
    """ Возвращает логическое значение при пересечении круга с прямоугольником """

    x = max(rectangle[0], min(center[0], rectangle[0]+rectangle[2]))
    y = max(rectangle[1], min(center[1], rectangle[1]+rectangle[3]))
    return sqrt((center[0]-x)**2+(center[1]-y)**2) <= radius


# Функция для проверки пересечения точки с повёрнутым прямоугольником:
def is_point_rot_rectangle_2d(point: tuple, rect: list, angle: float) -> bool:
    """ Возвращает логическое значение при пересечении точки с повёрнутым прямоугольником """

    sinrad, cosrad = sin(radians(angle)), cos(radians(angle))
    x = (point[0]-(rect[0]+rect[2]/2))*cosrad-(point[1]-(rect[1]+rect[3]/2))*sinrad
    y = (point[0]-(rect[0]+rect[2]/2))*sinrad+(point[1]-(rect[1]+rect[3]/2))*cosrad
    return abs(x) <= abs(rect[2])/2 and abs(y) <= abs(rect[3])/2


# Функция для проверки пересечения точки с прямоугольником:
def is_point_rectangle_2d(point: tuple, rect: list) -> bool:
    """ Возвращает логическое значение при пересечении точки с прямоугольником """

    return point[0] >= rect[0] and point[0] <= rect[0]+rect[2] and point[1] >= rect[1] and point[1] <= rect[1]+rect[3]


# Функция для проверки столкновения прямоугольника с прямоугольником:
def is_rectangle_rectangle_2d(r1: tuple, r2: tuple) -> bool:
    """ Возвращает логическое значение при пересечении прямоугольника с прямоугольником """

    return r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1]


# Функция для проверки пересечения точки с кругом:
def is_point_circle_2d(point: tuple, circle: tuple, radius: float) -> bool:
    """ Возвращает логическое значение при пересечении точки с кругом """

    return sqrt((point[0]-circle[0])**2+(point[1]-circle[1])**2) <= radius


# Функция для проверки пересечения точки с треугольником:
def is_point_triangle_2d(point: tuple, x1: float, y1: float, x2: float, y2: float, x3: float, y3: float) -> bool:
    """ Возвращает логическое значение при пересечении точки с треугольником """

    a = ((y2-y3)*(point[0]-x3)+(x3-x2)*(point[1]-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    b = ((y3-y1)*(point[0]-x3)+(x1-x3)*(point[1]-y3))/((y2-y3)*(x1-x3)+(x3-x2)*(y1-y3))
    return 0 <= a <= 1 and 0 <= b <= 1 and 0 <= (1-a-b) <= 1
