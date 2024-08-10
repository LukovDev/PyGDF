#
# utils.py - Содержит базовые полезные функции.
#


# Импортируем:
import copy
import pypresence
from .graphics.camera import Camera2D
from .math import *


# Discord Rich Presence реализация:
class DiscordRPC:
    def __init__(self, client_id: int = None) -> None:
        self.rpc = None
        self.connect(client_id)

    # Соединить с дискордом:
    def connect(self, client_id: int) -> "DiscordRPC":
        self.destroy()
        self.rpc = pypresence.Presence(str(client_id))
        self.rpc.connect()
        return self

    # Обновить статус:
    def update(self,
           state:       str   = None,  # Состояние, которое отображается в статусе. Например, "Играет в игру".
           details:     str   = None,  # Детали статуса. Например, "Подробности о игре".
           start_time:  int   = None,  # Начальное время активности в секундах UNIX-времени.
           end_time:    int   = None,  # Конечное время активности в секундах UNIX-времени.
           large_image: str   = None,  # Ключ большого изображения, которое будет отображаться в статусе.
           large_text:  str   = None,  # Текст, отображаемый при наведении на большое изображение.
           small_image: str   = None,  # Ключ маленького изображения, которое будет отображаться в статусе.
           small_text:  str   = None,  # Текст, отображаемый при наведении на маленькое изображение.
           party_id:    str   = None,  # Идентификатор группы (для социальных функций Discord).
           party_size:  tuple = None,  # Кортеж, содержащий текущий размер группы и максимальный размер группы.
           join_id:     str   = None,  # Ключ для присоединения к активности (для социальных функций Discord).
           match_id:    str   = None,  # Идентификатор матча (для игровых функций Discord).
           instance:    bool  = None   # Указывает, является ли активность инстансом (для игровых функций Discord).
           ) -> "DiscordRPC":

        # Передаём параметры в обновление статуса:
        self.rpc.update(
            state=state, details=details, start=start_time, end=end_time, large_image=large_image,
            large_text=large_text, small_image=small_image, small_text=small_text, party_id=party_id,
            party_size=party_size, join=join_id, match=match_id, instance=instance)
        return self

    # Отключиться от дискорда:
    def destroy(self) -> "DiscordRPC":
        if self.rpc is not None: self.rpc.close() ; self.rpc = None
        return self


# Утилиты для 2D вещей:
class Utils2D:
    # Получить позицию точки из окна в мировом пространстве:
    @staticmethod
    def local_to_global(camera: Camera2D, point: vec2) -> vec2:
        """ Переводит координаты точки на экране, в мировые координаты в 2D пространстве """

        # Позиция нижнего левого угла камеры с учётом метра и зума камеры:
        camera_posx = camera.position.x - ((camera.width  * camera.zoom) / 2) * (camera.meter / 100)
        camera_posy = camera.position.y - ((camera.height * camera.zoom) / 2) * (camera.meter / 100)

        # Позиция точки с учётом метра и зума камеры (Y координату точки инвертируем):
        point_posx = (+(point.x                ) * (camera.meter / 100)) * camera.zoom
        point_posy = (-(point.y - camera.height) * (camera.meter / 100)) * camera.zoom

        # Складываем и возвращаем результат:
        return vec2(camera_posx + point_posx, camera_posy + point_posy)

        """ Сокращённая версия выглядит так:
        # Для использования вам нужен экземпляр 2D камеры с названием camera и вектор точки с названием point.

        p, s, z, m = camera.position.xy, camera.size.xy, camera.zoom, camera.meter
        vec2(p.x-(s.x*z*m)/200+(point.x*m/100)*z, p.y-(s.y*z*m)/200-((point.y-s.y)*m/100)*z)
        """

    # Найти угол наклона из двух координат:
    @staticmethod
    def get_angle_points(point_1: vec2, point_2: vec2) -> float:
        """ Возвращает угол между первой и второй координатой """

        return -degrees(atan2(point_2.y - point_1.y, point_2.x - point_1.x))

    # Найти точку из угла и радиуса:
    @staticmethod
    def get_point_on_radius(radius: float, angle: float) -> vec2:
        """ Возвращает координаты в заданном радиусе и угле """

        return vec2(sin(radians(angle)) * radius, cos(radians(angle)) * radius)

    # Получить дельту для перемещения вектора в сторону направления на расстояние:
    @staticmethod
    def move_vector_on_direction(direction: vec2, distance: float) -> vec2:
        """ Возвращает 2 числа для перемещения вектора в сторону направления """

        point_on_rad = lambda a, d:   vec2(d * sin(radians(a)), d * cos(radians(a)))
        angle_points = lambda p1, p2: -degrees(atan2(p2.y - p1.y, p2.x - p1.x))
        return point_on_rad(angle_points(vec2(0, 0), normalize(direction)), distance)

    # Получить вектор направления из угла:
    @staticmethod
    def get_angle_in_direction(angle: float) -> vec2:
        """ Возвращает 2 числа в виде направления из угла """

        return vec2(-sin(radians(angle-90)), -cos(radians(angle-90)))

    # Получить скорость из вектора:
    @staticmethod
    def get_speed_vector(vector: vec2) -> float:
        """ Возвращает скорость в виде float значения из вектора """

        return sqrt(vector.x**2 + vector.y**2)


# 2D пересечения геометрических объектов:
class Intersects:
    # Проверяем пересекается ли окружность с прямоугольником:
    @staticmethod
    def circle_rectangle(center: vec2, radius: float, rect: list) -> bool:
        """ Возвращает логическое значение при пересечении круга с прямоугольником """

        x = max(rect[0], min(center[0], rect[0] + rect[2]))
        y = max(rect[1], min(center[1], rect[1] + rect[3]))
        return sqrt((center[0] - x) ** 2 + (center[1] - y) ** 2) <= radius

    # Функция для проверки пересечения круга с повёрнутым прямоугольником:
    @staticmethod
    def circle_rot_rectangle(center: vec2, radius: float, rect: list, angle: float) -> bool:
        """ Возвращает логическое значение при пересечении круга с повёрнутым прямоугольником """

        rdx = center[0]-(rect[0]+rect[2]/2)*cos(radians(angle))-(center[1]-(rect[1]+rect[3]/2))*sin(radians(angle))
        rdy = center[0]-(rect[0]+rect[2]/2)*sin(radians(angle))+(center[1]-(rect[1]+rect[3]/2))*cos(radians(angle))
        c = max(rect[0], min(rect[0]+rect[2], rect[0]+rdx)), max(rect[1], min(rect[1]+rect[3], rect[1]+rdy))
        return sqrt((rdx - (c[0] - rect[0]))**2 + (rdy - (c[1] - rect[1]))**2) <= radius

    # Функция для проверки столкновения прямоугольника с прямоугольником:
    @staticmethod
    def rectangle_rectangle(r1: list, r2: list) -> bool:
        """ Возвращает логическое значение при пересечении прямоугольника с прямоугольником """

        return r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1]

    # Функция для проверки пересечения точки с прямоугольником:
    @staticmethod
    def point_rectangle(point: vec2, rect: list) -> bool:
        """ Возвращает логическое значение при пересечении точки с прямоугольником """

        return point.x >= rect[0] and point.x <= rect[0]+rect[2] and point.y >= rect[1] and point.y <= rect[1]+rect[3]

    # Функция для проверки пересечения точки с повёрнутым прямоугольником:
    @staticmethod
    def point_rot_rectangle(point: vec2, rect: list, angle: float) -> bool:
        """ Возвращает логическое значение при пересечении точки с повёрнутым прямоугольником """

        sinrad, cosrad = sin(radians(angle)), cos(radians(angle))
        x = (point[0]-(rect[0]+rect[2]/2))*cosrad-(point[1]-(rect[1]+rect[3]/2))*sinrad
        y = (point[0]-(rect[0]+rect[2]/2))*sinrad+(point[1]-(rect[1]+rect[3]/2))*cosrad
        return abs(x) <= abs(rect[2])/2 and abs(y) <= abs(rect[3])/2

    # Функция для проверки пересечения круга с кругом:
    @staticmethod
    def circle_circle(center1: vec2, radius1: float, center2: vec2, radius2: float) -> bool:
        """ Возвращает логическое значение при пересечении круга с кругом """

        # Если расстояние меньше или равно сумме радиусов, то круги пересекаются:
        return length(center2 - center1) <= (radius1 + radius2)

    # Функция для проверки пересечения точки с кругом:
    @staticmethod
    def point_circle(point: vec2, circle: vec2, radius: float) -> bool:
        """ Возвращает логическое значение при пересечении точки с кругом """

        return sqrt((point.x - circle.x) ** 2 + (point.y - circle.y) ** 2) <= radius

    # Функция для проверки пересечения точки с треугольником:
    @staticmethod
    def point_triangle(point: vec2, verts: list) -> bool:
        """ Возвращает логическое значение при пересечении точки с треугольником """

        a, b, c = verts
        denom = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        a1 = ((b[1] - c[1]) * (point.x - c[0]) + (c[0] - b[0]) * (point.y - c[1])) / denom
        b1 = ((c[1] - a[1]) * (point.x - c[0]) + (a[0] - c[0]) * (point.y - c[1])) / denom
        return 0 <= a1 <= 1 and 0 <= b1 <= 1 and 0 <= (1 - a1 - b1) <= 1
