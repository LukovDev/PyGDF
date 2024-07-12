#
# phys2d.py - Создаёт реализацию 2D физики.
#


# Импортируем:
if True:
    import pymunk
    from ..math import *
    from ..utils import Utils2D


# Ошибка физики:
class PhysicsError(Exception): pass


# 2D физика:
class Physics2D:
    # Динамическое тело:
    DYNAMIC = pymunk.Body.DYNAMIC

    # Кинематическое тело:
    KINEMATIC = pymunk.Body.KINEMATIC

    # Статическое тело:
    STATIC = pymunk.Body.STATIC

    # Физическое тело:
    class Body(pymunk.Body):  pass

    # Физическая форма:
    class Shape(pymunk.Shape): pass
    
    # Фильтр физической формы:
    class ShapeFilter(pymunk.ShapeFilter): pass

    # Структура для всех найденных физических объектов:
    class FindedObject:
        def __init__(self, object: "Physics2D.Objects", distance: float, point: vec2) -> None:
            self.object   = object
            self.distance = distance
            self.point    = point

    # Физические объекты:
    class Objects:
        # Общий родительский класс физических объектов:
        class SimplePhysicsObject:
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                self.mass        = mass                # Масса объекта.
                self.elasticity  = elasticity          # Сила упругости.
                self.friction    = friction            # Сила трения.
                self.body_type   = body_type           # Тип объекта.
                self.max_vel     = float(max_vel)      # Максимальная скорость перемещения.
                self.max_ang_vel = float(max_ang_vel)  # Максимальная скорость вращения.
                self.meter       = 100.0               # Единица измерения.
                self.body        = None                # Тело объекта.
                self.shape       = None                # Форма объекта.

            @property
            def position(self) -> vec2: return self.get_position()

            @property
            def angle(self) -> vec2: return self.get_angle()

            @property
            def speed(self) -> float: return Utils2D.get_speed_vector(self.velocity)

            @property
            def space(self) -> pymunk.Space: return self.body.space

            # Установить позицию объекта:
            def set_position(self, position: vec2) -> "Physics2D.Objects":
                self.body.position = tuple(position.xy)
                return self

            # Получить позицию объекта:
            def get_position(self) -> vec2:
                return vec2(self.body.position)

            # Установить угол наклона объекта:
            def set_angle(self, angle: float) -> "Physics2D.Objects":
                self.body.angle = radians(-angle)
                return self

            # Получить угол наклона объекта:
            def get_angle(self) -> float:
                return -degrees(self.body.angle)

            # Установить скорость перемещения объекта:
            def set_velocity(self, velocity: vec2) -> "Physics2D.Objects":
                self.body.velocity = tuple(velocity.xy)
                return self

            # Получить скорость перемещения объекта:
            def get_velocity(self) -> vec2:
                return vec2(self.body.velocity)

            # Установить угловую скорость:
            def set_torque(self, torque: float) -> "Physics2D.Objects":
                self.body.angular_velocity = -radians(torque)
                return self

            # Получить угловую скорость:
            def get_torque(self) -> float:
                return self.body.angular_velocity

            # Установить максимальную скорость перемещения:
            def set_max_velocity(self, max_vel: float) -> "Physics2D.Objects":
                self.max_vel = float(max_vel)
                return self

            # Установить максимальную скорость вращения:
            def set_max_ang_velocity(self, max_ang_vel: float) -> "Physics2D.Objects":
                self.max_ang_vel = float(max_ang_vel)
                return self

            # Получить соединения объекта:
            def get_constraints(self) -> list:
                return list(self.body.constraints)

            # Применить силу к этому телу:
            def add_force_local(self, force: vec2, point: vec2 = vec2(0)) -> "Physics2D.Objects":
                self.body.apply_force_at_local_point(tuple(force.xy*KG_N*self.meter), tuple(point))
                return self

            # Применить силу к этому телу в мировых координатах:
            def add_force_global(self, force: vec2, point: vec2 = vec2(0)) -> "Physics2D.Objects":
                self.body.apply_force_at_world_point(tuple(force.xy*KG_N*self.meter), tuple(point))
                return self

            # Применить импульс к этому телу:
            def add_impulse_local(self, impulse: vec2, point: vec2 = vec2(0)) -> "Physics2D.Objects":
                self.body.apply_impulse_at_local_point(tuple(impulse.xy*KG_N*self.meter), tuple(point))
                return self

            # Применить импульс к этому телу в мировых координатах:
            def add_impulse_global(self, impulse: vec2, point: vec2 = vec2(0)) -> "Physics2D.Objects":
                self.body.apply_impulse_at_world_point(tuple(impulse.xy*KG_N*self.meter), tuple(point))
                return self

            # Функция ограничения скорости вращения и перемещения:
            def __limit_velocity_func__(self) -> any:
                def limit_velocity(body, gravity, damping, dt) -> None:
                    pymunk.Body.update_velocity(body, gravity, damping, dt)
                    if body.velocity.length > (self.max_vel*KG_N*self.meter):
                        body.velocity *= ((self.max_vel*KG_N*self.meter) / body.velocity.length)
                    if abs(body.angular_velocity) > self.max_ang_vel:
                        if body.angular_velocity < 0: body.angular_velocity = radians(self.max_ang_vel)
                        else: body.angular_velocity = -radians(self.max_ang_vel)
                return limit_velocity

        # Класс тела (без формы):
        class Empty(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                self.body          = pymunk.Body(mass, body_type=body_type)
                self.body.position = tuple(position.xy)
                self.body.angle    = -radians(angle)

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()

        # Класс прямоугольника (квадрата):
        class Square(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         size:        vec2  = vec2(1, 1),
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                self.size               = vec2(abs(size.x), abs(size.y))
                self.body               = pymunk.Body(mass, pymunk.moment_for_box(mass, size), body_type)
                self.body.position      = tuple(position.xy)
                self.body.angle         = -radians(angle)
                self.shape              = pymunk.Poly.create_box(self.body, size)
                self.shape.elasticity   = self.elasticity
                self.shape.friction     = self.friction

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()

            # Получить вершины формы:
            def get_vertices(self) -> list:
                return [vec2(v) for v in self.shape.get_vertices()]

        # Класс идеально ровного круга:
        class Circle(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         radius:      float = 1.0,
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                self.radius           = abs(radius)
                self.body             = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -radians(angle)
                self.shape            = pymunk.Circle(self.body, radius)
                self.shape.elasticity = self.elasticity
                self.shape.friction   = self.friction

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()

            @property
            def size(self) -> vec2: return vec2(self.radius*2)

        # Класс треугольника:
        class Triangle(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         size:        vec2  = vec2(1, 1),
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                vertices = [
                    (-size.x/2, -sqrt(3) / 2 * size.y/2),
                    (+size.x/2, -sqrt(3) / 2 * size.y/2),
                    (+0,        +sqrt(3) / 2 * size.y/2)
                ]
                self.size             = vec2(abs(size.x), abs(size.y))
                self.body             = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -radians(angle)
                self.shape            = pymunk.Poly(self.body, vertices)
                self.shape.elasticity = elasticity
                self.shape.friction   = friction

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()

            # Получить вершины формы:
            def get_vertices(self) -> list:
                return [vec2(v) for v in self.shape.get_vertices()]

        # Класс выпуклого многоугольника:
        class Poly(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         vertices:    list  = None,
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                if vertices is None: vertices = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]
                else:                vertices = [tuple(vert.xy) for vert in vertices]
                self.body             = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -radians(angle)
                self.shape            = pymunk.Poly(self.body, vertices)
                self.shape.elasticity = elasticity
                self.shape.friction   = friction

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()

            # Получить вершины формы:
            def get_vertices(self) -> list:
                return [vec2(v) for v in self.shape.get_vertices()]

        # Класс линии:
        class Segment(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         point_1:     vec2  = vec2(-1, 0),
                         point_2:     vec2  = vec2(+1, 0),
                         radius:      float = 1.0,
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                self.points           = [tuple(point_1.xy), tuple(point_2.xy)]
                self.radius           = radius
                self.body             = pymunk.Body(mass, pymunk.moment_for_poly(mass, self.points), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = atan2(point_2.y - point_1.y, point_2.x - point_1.x) - radians(angle)
                self.shape            = pymunk.Segment(self.body, tuple(point_1.xy), tuple(point_2.xy), radius)
                self.shape.elasticity = self.elasticity
                self.shape.friction   = self.friction

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()

            # Получить вершины формы:
            def get_vertices(self) -> list:
                return [vec2(p) for p in self.points]

        # Класс многоугольника:
        class Mesh(SimplePhysicsObject):
            def __init__(self,
                         mass:        float = 1.0,
                         elasticity:  float = 0.2,
                         friction:    float = 0.9,
                         position:    vec2  = vec2(0, 0),
                         vertices:    list  = None,
                         radius:      float = 1.0,
                         angle:       float = 0.0,
                         body_type:   int   = pymunk.Body.DYNAMIC,
                         max_vel:     float = float("inf"),
                         max_ang_vel: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, body_type, max_vel, max_ang_vel)
                if vertices is None: vertices = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]
                else:                vertices = [tuple(vert.xy) for vert in vertices]
                self.vertices      = vertices
                self.body          = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position = tuple(position.xy)
                self.body.angle    = -radians(angle)
                self.shapes        = []

                if not (max_vel == float("inf") and max_ang_vel == float("inf")):
                    self.body.velocity_func = self.__limit_velocity_func__()
                
                # Создаём набор сегментов исходя из вершин:
                for index in range(len(vertices)):
                    shape = pymunk.Segment(self.body, vertices[index], vertices[(index + 1) % len(vertices)], radius)
                    shape.elasticity = elasticity
                    shape.friction   = friction
                    self.shapes.append(shape)

            # Получить вершины формы:
            def get_vertices(self) -> list:
                return [vec2(v) for v in self.vertices]

    # Классы ограничителей объекта:
    class Constraints:
        # Родительский класс:
        class SimpleConstraint:
            def __init__(self,
                         constraint:   pymunk.Constraint,
                         max_force:    float = float("inf"),
                         bias_coef:    float = float("inf"),
                         is_collision: bool  = True) -> None:
                self.constraint           = constraint        # Связь между двух объектов.
                self.constraint.max_force = max_force * KG_N  # Максимальная сила, которую может приложить constraint.
                self.constraint.bias_coef = bias_coef * KG_N  # Скорость, с которой исправляется ошибка constraint.

                # Должны ли два тела сталкиваться:
                self.constraint._set_collide_bodies(is_collision)

            # Получить вершины соединения:
            def get_vertices(self) -> list:
                vertices = []
                if isinstance(self.constraint, pymunk.SimpleMotor):
                    return [vec2(self.constraint.a.position), vec2(self.constraint.b.position)]
                for obj in [self.constraint.a, self.constraint.b]:
                    x, y = self.constraint.anchor_a if obj == self.constraint.a else self.constraint.anchor_b
                    cos_a, sin_a = cos(obj.angle), sin(obj.angle)
                    rotated_x, rotated_y = x * cos_a - y * sin_a, x * sin_a + y * cos_a
                    vertices.append(vec2(obj.position[0] + rotated_x, obj.position[1] + rotated_y))
                return vertices

        # Удерживает две точки на двух телах вместе, но позволяет им вращаться относительно друг друга:
        class PinJoint(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         point_a:      vec2,                  # Точка на объекте A.
                         point_b:      vec2,                  # Точка на объекте B.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.PinJoint(a.body, b.body, tuple(point_a.xy), tuple(point_b.xy))
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Позволяет двум точкам на двух телах скользить относительно друг друга в пределах заданного диапазона:
        class SlideJoint(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         point_a:      vec2,                  # Точка на объекте A.
                         point_b:      vec2,                  # Точка на объекте B.
                         min_dst:      float,                 # Минимальное расстояние.
                         max_dst:      float,                 # Максимальное расстояние.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.SlideJoint(a.body, b.body, tuple(point_a.xy), tuple(point_b.xy), min_dst, max_dst)
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Удерживает две точки на двух телах вместе позволяя им вращаться относительно друг друга вокруг точки поворота:
        class PivotJoint(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         point:        vec2,                  # Общая точка.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.PivotJoint(a.body, b.body, tuple(point.xy))
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Позволяет точке на одном теле скользить вдоль отрезка линии на другом теле:
        class GrooveJoint(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         point_a:      vec2,                  # Начало отрезка линии.
                         point_b:      vec2,                  # Конец отрезка линии.
                         anchor_b:     vec2,                  # Точка крепления на втором теле.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.GrooveJoint(a.body, b.body, tuple(point_a.xy), tuple(point_b.xy), tuple(anchor_b))
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Создать пружинистое соединение между двумя объектами:
        class DampedSpring(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         point_a:      vec2,                  # Точка на объекте A.
                         point_b:      vec2,                  # Точка на объекте B.
                         rest_length:  float,                 # Длина покоя пружины.
                         stiffness:    float,                 # Жесткость пружины (кг).
                         damping:      float,                 # Коэффициент демпфирования.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.DampedSpring(
                    a.body, b.body, tuple(point_a.xy), tuple(point_b.xy), rest_length, stiffness*KG_N, damping)
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Создать пружинистое вращательное соединение между двумя объектами:
        class DampedRotarySpring(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         rest_angle:   float,                 # Угол покоя между двумя телами.
                         stiffness:    float,                 # Жесткость пружины (кг).
                         damping:      float,                 # Коэффициент демпфирования.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.DampedRotarySpring(a.body, b.body, -radians(rest_angle), stiffness*KG_N, damping)
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Ограничивает относительное вращение двух тел:
        class RotaryLimitJoint(SimpleConstraint):
            def __init__(self,
                         a:           "Physics2D.Objects",    # Объект A.
                         b:           "Physics2D.Objects",    # Объект B.
                         min_ang:      float,                 # Минимальный относительный угол между телами.
                         max_ang:      float,                 # Максимальный относительный угол между телами.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.RotaryLimitJoint(a.body, b.body, -radians(min_ang), -radians(max_ang))
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Позволяет относительное вращение между двумя телами в стиле трещотки:
        class RatchetJoint(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         phase:        float,                 # Начальная фаза трещотки (угол).
                         ratchet:      float,                 # Расстояние между позициями трещотки (угол).
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.RatchetJoint(a.body, b.body, -radians(phase), -radians(ratchet))
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Создать шестерёнестое соединение между двумя объектами:
        class GearJoint(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         phase:        float,                 # Начальная фаза трещотки (угол).
                         ratio:        float,                 # Соотношение угловых скоростей.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.GearJoint(a.body, b.body, -radians(phase), -radians(ratio))
                super().__init__(constraint, max_force, bias_coef, is_collision)

        # Создать двигательное соединение между двумя объектами:
        class SimpleMotor(SimpleConstraint):
            def __init__(self,
                         a:            "Physics2D.Objects",   # Объект A.
                         b:            "Physics2D.Objects",   # Объект B.
                         rps:          float = 1.0,           # Количество оборотов в секунду.
                         max_force:    float = float("inf"),  # Максимальная сила, которую может приложить constraint.
                         bias_coef:    float = float("inf"),  # Скорость, с которой исправляется ошибка constraint.
                         is_collision: bool  = True           # Должны ли два тела сталкиваться.
                         ) -> None:
                constraint = pymunk.SimpleMotor(a.body, b.body, -(2*math.pi)*rps)
                super().__init__(constraint, max_force, bias_coef, is_collision)

    # Пространство симуляции:
    class Space:
        def __init__(self,
                     gravity:        vec2  = vec2(0),
                     phys_speed:     float = 1.0,
                     meter:          float = 100.0,
                     damping:        float = 1.0,
                     iterations:     int   = 64,
                     idle_speed:     float = 0.0,
                     sleep_time:     float = float("inf"),
                     collision_slop: float = 0.01,
                     collision_bias: float = 0.75
                     ) -> None:
            self.space       = pymunk.Space()   # Физическое пространство.
            self.phys_speed  = abs(phys_speed)  # Скорость симуляции физики.
            self.meter       = meter            # Единица измерения.
            self.__old_dt__  = 1/60             # Прошлое время кадра.
            self.objects     = []               # Список всех физических объектов.
            self.constraints = []               # Список всех соединений.

            # Устанавливаем параметры:
            self.set_gravity(gravity)                # Установить гравитацию.
            self.set_damping(damping)                # Установить силу трения об воздух.
            self.set_iterations(iterations)          # Установить количество итераций обработки столкновений за шаг.
            self.set_idle_speed(idle_speed)          # Установить порог скорости объекта, после он считается статичным.
            self.set_sleep_time(sleep_time)          # Установить порог времени статичности объекта, после он засыпает.
            self.set_collision_slop(collision_slop)  # Установить допустимое смещение при столкновении объектов.
            self.set_collision_bias(collision_bias)  # Установить процентное количество исправлений ошибок сталкиваний.

        # Шаг симуляции:
        def step(self, delta_time: float) -> None:
            self.space.step(delta_time)

        # Обновление физики:
        def update(self, delta_time: float) -> None:
            # Нельзя допустить чтобы скорость физики была в минусе:
            self.phys_speed = abs(self.phys_speed)

            # Если новый dt больше старого в 2 раза, то используем старый dt. А также ограничиваем dt до 1/10 кадра:
            dt = min(self.__old_dt__ if delta_time > self.__old_dt__ * 2 else delta_time, 1/10)
            self.__old_dt__ = delta_time

            # Шаг симуляции:
            self.step(dt*self.phys_speed)

        # Добавить новый объект в пространство:
        def add(self, object: "Physics2D.Objects") -> None:
            for obj in [object] if not isinstance(object, list) else object:
                # Если это ограничитель:
                if issubclass(type(obj), Physics2D.Constraints.SimpleConstraint):
                    self.space.add(obj.constraint)
                    self.constraints.append(obj)
                    continue

                # Если это объект:
                if isinstance(obj, Physics2D.Objects.Mesh): self.space.add(obj.body, *obj.shapes)
                elif obj.body is None: continue
                elif obj.shape is None: self.space.add(obj.body)
                else: self.space.add(obj.body, obj.shape)
                obj.meter = self.meter

                # Удаляем объект из списка объектов:
                if obj not in self.objects:
                    self.objects.append(obj)

        # Удалить объект из пространства:
        def remove(self, object: "Physics2D.Objects") -> None:
            for obj in [object] if not isinstance(object, list) else object:
                # Если это ограничитель:
                if issubclass(type(obj), Physics2D.Constraints.SimpleConstraint):
                    self.space.remove(obj.constraint)
                    self.constraints.remove(obj)
                    continue

                # Если это объект:
                if isinstance(obj, Physics2D.Objects.Mesh): self.space.remove(obj.body, *obj.shapes)
                elif obj.body is None: continue
                elif obj.shape is None: self.space.remove(obj.body)
                else: self.space.remove(obj.body, obj.shape)
                obj.meter = 100.0

                # Удаляем объект из списка объектов:
                if obj in self.objects:
                    self.objects.remove(obj)

                # Проходимся по списку ограничителей у тела, и удаляем те ограничители, что были привязаны к нему:
                for constraint in obj.body.constraints:
                    if constraint in self.space.constraints:
                        self.space.remove(constraint)
                        self.constraints = [c for c in self.constraints if c.constraint != constraint]

        # Установить гравитацию:
        def set_gravity(self, gravity: vec2) -> "Physics2D.Space":
            self.space.gravity = tuple(gravity.xy * self.meter)
            return self

        # Получить гравитацию:
        def get_gravity(self) -> vec2:
            return vec2(self.space.gravity * self.meter)

        # Установить силу трения об воздух:
        def set_damping(self, damping: float) -> "Physics2D.Space":
            self.space.damping = float(damping)
            return self

        # Получить силу трения об воздух:
        def get_damping(self) -> float:
            return self.space.damping

        # Установить количество итераций обработки столкновений за шаг:
        def set_iterations(self, iterations: int) -> "Physics2D.Space":
            self.space.iterations = int(iterations)
            return self

        # Получить количество итераций обработки столкновений за шаг:
        def get_iterations(self) -> int:
            return self.space.iterations

        # Установить порог скорости объекта, после которого он считается статичным:
        def set_idle_speed(self, idle_speed: float) -> "Physics2D.Space":
            self.space.idle_speed_threshold = float(idle_speed)
            return self

        # Получить порог скорости объекта, после которого он считается статичным:
        def get_idle_speed(self) -> float:
            return self.space.idle_speed_threshold

        # Установить порог времени статичности объекта, после которого он засыпает:
        def set_sleep_time(self, sleep_time: float) -> "Physics2D.Space":
            self.space.sleep_time_threshold = float(sleep_time)
            return self

        # Получить порог времени статичности объекта, после которого он засыпает:
        def get_sleep_time(self) -> float:
            return self.space.sleep_time_threshold

        # Установить допустимое смещение при столкновении объектов:
        def set_collision_slop(self, collision_slop: float) -> "Physics2D.Space":
            self.space.collision_slop = collision_slop * self.meter
            return self

        # Получить допустимое смещение при столкновении объектов:
        def get_collision_slop(self) -> float:
            return self.space.collision_slop

        # Установить процентное количество исправлений ошибок сталкиваний:
        def set_collision_bias(self, collision_bias: float) -> "Physics2D.Space":
            self.space.collision_bias = ((1.0 - collision_bias) ** 60) * self.meter
            return self

        # Получить процентное количество исправлений ошибок сталкиваний:
        def get_collision_bias(self) -> float:
            return self.space.collision_bias

        # Найти ближайший объект:
        def find_nearest_object(self, point: vec2, max_dst: float,
                                shape_filter: pymunk.ShapeFilter = pymunk.ShapeFilter()) -> list:
            info = self.space.point_query_nearest(tuple(point.xy), max_dst, shape_filter)
            if info is None: return None
            obj = next((c for c in self.objects if getattr(c, "body", None) == info.shape.body), None)
            return Physics2D.FindedObject(obj, float(info.distance), vec2(info.point)) if obj is not None else None

        # Найти все объекты в области:
        def find_objects(self, point: vec2, max_dst: float,
                         shape_filter: pymunk.ShapeFilter = pymunk.ShapeFilter()) -> list:
            fnddobj = []
            objects = []
            
            info_list = self.space.point_query(tuple(point.xy), max_dst, shape_filter)
            if info_list is None: return None

            for info in info_list:
                obj = next((c for c in self.objects if getattr(c, "body", None) == info.shape.body), None)
                if obj is None: continue
                if obj not in objects:
                    objects.append(obj)
                    fnddobj.append(Physics2D.FindedObject(obj, float(info.distance), vec2(info.point)))

            return fnddobj if fnddobj else None
