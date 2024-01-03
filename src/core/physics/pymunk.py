#
# pymunk.py - Создаёт реализацию обёртки для этой библиотеки.
#


# Импортируем:
if True:
    import pymunk
    from ..math import *
    from ..graphics.gl import *


# Класс означающий, что мы обращаемся к реализации физики от pymunk:
class PyMunk:
    # Классы-обёртки:
    if True:
        class Space              (pymunk.Space):              pass
        class Body               (pymunk.Body):               pass
        class Shape              (pymunk.Shape):              pass
        class ShapeFilter        (pymunk.ShapeFilter):        pass
        class Circle             (pymunk.Circle):             pass
        class Poly               (pymunk.Poly):               pass
        class Segment            (pymunk.Segment):            pass
        class Constraint         (pymunk.Constraint):         pass
        class PinJoint           (pymunk.PinJoint):           pass
        class SlideJoint         (pymunk.SlideJoint):         pass
        class PivotJoint         (pymunk.PivotJoint):         pass
        class GrooveJoint        (pymunk.GrooveJoint):        pass
        class DampedSpring       (pymunk.DampedSpring):       pass
        class DampedRotarySpring (pymunk.DampedRotarySpring): pass
        class RotaryLimitJoint   (pymunk.RotaryLimitJoint):   pass
        class RatchetJoint       (pymunk.RatchetJoint):       pass
        class GearJoint          (pymunk.GearJoint):          pass
        class SimpleMotor        (pymunk.SimpleMotor):        pass

    # Игровые объекты:
    class Objects:
        # Родительский класс:
        class BaseGameObject:
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                self.mass                 = mass
                self.elasticity           = elasticity
                self.friction             = friction
                self.max_velocity         = max_velocity
                self.max_angular_velocity = max_angular_velocity
                self.body_type            = body_type
                self.body                 = None
                self.shape                = None

            @property
            def position(self) -> vec2: return vec2(self.body.position)

            @property
            def angle(self) -> float: return -math.degrees(self.body.angle)

            @property
            def velocity(self) -> tuple: return self.body.velocity

            @property
            def angular_velocity(self) -> float: return self.body.angular_velocity

            @property
            def constraints(self) -> list: return list(self.body.constraints)

            # Применить силу к этому телу:
            def apply_force(self, force: tuple, point: tuple = (0, 0)) -> None:
                self.body.apply_force_at_local_point(force, point)

            # Применить силу к этому телу в мировых координатах:
            def apply_world_force(self, force: tuple, point: tuple = (0, 0)) -> None:
                self.body.apply_force_at_world_point(force, point)

            # Применить импульс к этому телу:
            def apply_impulse(self, impulse: tuple, point: tuple = (0, 0)) -> None:
                self.body.apply_impulse_at_local_point(impulse, point)

            # Применить импульс к этому телу в мировых координатах:
            def apply_world_impulse(self, impulse: tuple, point: tuple = (0, 0)) -> None:
                self.body.apply_impulse_at_world_point(impulse, point)

            # Установить крутящий момент:
            def set_torque(self, torque: float) -> None: self.body.angular_velocity = -math.radians(torque)

            # # Функция ограничения скорости вращения и перемещения:
            # def __limit_velocity_func__(self):
            #     def limit_velocity(body, gravity, damping, dt) -> None:
            #         pymunk.Body.update_velocity(body, gravity, damping, dt)
            #         if body.velocity.length > self.max_velocity:
            #             body.velocity *= (self.max_velocity / body.velocity.length)
            #         if abs(body.angular_velocity) > self.max_angular_velocity:
            #             if body.angular_velocity < 0: body.angular_velocity = math.radians(self.max_angular_velocity)
            #             else: body.angular_velocity = -math.radians(self.max_angular_velocity)
            #     return limit_velocity

        # Класс прямоугольника (квадрата):
        class Square(BaseGameObject):
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         size:                 tuple = (1, 1),
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, position,
                                 angle, body_type, max_velocity, max_angular_velocity)
                self.size             = abs(size[0]), abs(size[1])
                self.body             = pymunk.Body(mass, pymunk.moment_for_box(mass, size), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -math.radians(angle)
                self.shape            = pymunk.Poly.create_box(self.body, size)
                self.shape.elasticity = self.elasticity
                self.shape.friction   = self.friction
                # self.body.velocity_func = self.__limit_velocity_func__()

            @property
            def vertices(self) -> list: return self.shape.get_vertices()

        # Класс треугольника:
        class Triangle(BaseGameObject):
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         size:                 tuple = (1, 1),
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, position,
                                 angle, body_type, max_velocity, max_angular_velocity)
                vertices = [
                    (-size[0]/2, -math.sqrt(3) / 2 * size[1]/2),
                    (+size[0]/2, -math.sqrt(3) / 2 * size[1]/2),
                    (+0,         +math.sqrt(3) / 2 * size[1]/2)
                ]
                self.body             = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -math.radians(angle)
                self.shape            = pymunk.Poly(self.body, vertices)
                self.shape.elasticity = elasticity
                self.shape.friction   = friction
                # self.body.velocity_func = self.__limit_velocity_func__()

            @property
            def vertices(self) -> list: return self.shape.get_vertices()

        # Класс идеально ровного круга:
        class Circle(BaseGameObject):
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         radius:               float = 1.0,
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, position,
                                 angle, body_type, max_velocity, max_angular_velocity)
                self.radius           = abs(radius)
                self.body             = pymunk.Body(mass, pymunk.moment_for_circle(mass, 0, radius), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -math.radians(angle)
                self.shape            = pymunk.Circle(self.body, radius)
                self.shape.elasticity = self.elasticity
                self.shape.friction   = self.friction
                # self.body.velocity_func = self.__limit_velocity_func__()

        # Класс выпуклого многоугольника:
        class Poly(BaseGameObject):
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         vertices:             list  = None,
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, position,
                                 angle, body_type, max_velocity, max_angular_velocity)
                if vertices is None: vertices = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]
                self.body             = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = -math.radians(angle)
                self.shape            = pymunk.Poly(self.body, vertices)
                self.shape.elasticity = elasticity
                self.shape.friction   = friction
                # self.body.velocity_func = self.__limit_velocity_func__()

            @property
            def vertices(self) -> list: return self.shape.get_vertices()

        # Класс линии:
        class Segment(BaseGameObject):
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         vertices:             list  = None,
                         radius:               float = 1.0,
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, position,
                                 angle, body_type, max_velocity, max_angular_velocity)
                if vertices is None: vertices = [(-1, 0), (1, 0)]
                rads = math.atan2(vertices[1][1] - vertices[0][1], vertices[1][0] - vertices[0][0])
                self.vertices         = vertices
                self.radius           = radius
                self.body             = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = rads - math.radians(angle)
                self.shape            = pymunk.Segment(self.body, vertices[0], vertices[1], radius)
                self.shape.elasticity = self.elasticity
                self.shape.friction   = self.friction
                # self.body.velocity_func = self.__limit_velocity_func__()

        # Класс многоугольника:
        class Mesh(BaseGameObject):
            def __init__(self,
                         mass:                 float = 1.0,
                         elasticity:           float = 0.2,
                         friction:             float = 0.9,
                         position:             vec2  = vec2(0, 0),
                         vertices:             list  = None,
                         radius:               float = 0.0,
                         angle:                float = 0.0,
                         body_type:            int   = pymunk.Body.DYNAMIC,
                         max_velocity:         float = float("inf"),
                         max_angular_velocity: float = float("inf")) -> None:
                super().__init__(mass, elasticity, friction, position,
                                 angle, body_type, max_velocity, max_angular_velocity)
                if vertices is None: vertices = [(-0.5, -0.5), (-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)]
                self.vertices      = vertices
                self.body          = pymunk.Body(mass, pymunk.moment_for_poly(mass, vertices), body_type)
                self.body.position = tuple(position.xy)
                self.body.angle    = -math.radians(angle)
                self.shapes        = []
                # self.body.velocity_func = self.__limit_velocity_func__()
                
                # Создаём набор сегментов исходя из вершин:
                for index in range(len(vertices)):
                    shape = pymunk.Segment(self.body, vertices[index], vertices[(index + 1) % len(vertices)], radius)
                    shape.elasticity = elasticity
                    shape.friction   = friction
                    self.shapes.append(shape)

    # Классы ограничители:
    class Constraints:
        # Родительский класс:
        class BaseConstraintObject:
            @property
            def vertices(self) -> list:
                vertices = []
                for obj in [self.constraint.a, self.constraint.b]:
                    x, y = self.constraint.anchor_a if obj == self.constraint.a else self.constraint.anchor_b
                    cos_a, sin_a = math.cos(obj.angle), math.sin(obj.angle)
                    rotated_x, rotated_y = x * cos_a - y * sin_a, x * sin_a + y * cos_a
                    vertices.append((obj.position[0] + rotated_x, obj.position[1] + rotated_y))
                return vertices

        # Создать жёсткое соединение между двумя объектами:
        class PinJoint(BaseConstraintObject):
            def __init__(self, a, b, anchor_a: tuple, anchor_b: tuple, bias_coef: float = 0.1,
                         max_bias: float = float("inf"), max_force: float = float("inf"),
                         collision_on: bool = True) -> None:
                self.constraint = pymunk.PinJoint(a.body, b.body, anchor_a, anchor_b)
                self.constraint.bias_coef = bias_coef
                self.constraint.max_bias = max_bias
                self.constraint.max_force = max_force
                self.constraint.collision_on = collision_on
                a.body.space.add(self.constraint)

        # Создать жёсткое соединение между двумя объектами с минимальной и максимальной длиной:
        class SlideJoint(BaseConstraintObject):
            def __init__(self, a, b, anchor_a: tuple, anchor_b: tuple, min: float = 50.0, max: float = 100.0,
                         max_force: float = float("inf"), collision_on: bool = True) -> None:
                self.constraint = pymunk.SlideJoint(a.body, b.body, anchor_a, anchor_b, min, max)
                self.constraint.max_force = max_force
                self.constraint.collision_on = collision_on
                a.body.space.add(self.constraint)

        # Создать соединение между двумя объектами вокруг одной точки:
        class PivotJoint(BaseConstraintObject):
            def __init__(self, a, b, anchor: tuple, bias_coef: float = 0.1,
                         max_bias: float = float("inf"), collide_bodies: bool = True) -> None:
                self.constraint = pymunk.PivotJoint(a.body, b.body, anchor)
                self.constraint.bias_coef = bias_coef
                self.constraint.max_bias = max_bias
                self.constraint.collide_bodies = collide_bodies
                a.body.space.add(self.constraint)

        # Создать ограничение движение одного тела вдоль заданной протяженности:
        class GrooveJoint(BaseConstraintObject):
            def __init__(self, a, b, groove1: tuple, groove2: tuple, anchor: tuple, bias_coef: float = 0.1,
                         max_bias: float = float("inf"), collide_bodies: bool = True) -> None:
                self.constraint = pymunk.GrooveJoint(a.body, b.body, groove1, groove2, anchor)
                self.constraint.bias_coef = bias_coef
                self.constraint.max_bias = max_bias
                self.constraint.collide_bodies = collide_bodies
                a.body.space.add(self.constraint)

        # Создать пружинистое соединение между двумя объектами:
        class DampedSpring(BaseConstraintObject):
            def __init__(self, a, b, anchor_a: tuple, anchor_b: tuple, rest_length: float = 100.0,
                         stiffness: float = 100.0, damping: float = 0.3) -> None:
                self.constraint = pymunk.DampedSpring(
                    a.body, b.body, anchor_a, anchor_b, rest_length, stiffness, damping)
                a.body.space.add(self.constraint)

        # Создать пружинистое вращательное соединение между двумя объектами:
        class DampedRotarySpring(BaseConstraintObject):
            def __init__(self, a, b, rest_angle: float = 0.0, stiffness: float = 100.0, damping: float = 0.3) -> None:
                self.constraint = pymunk.DampedRotarySpring(
                    a.body, b.body, -math.radians(rest_angle), stiffness, damping)
                a.body.space.add(self.constraint)

        # Создать ограничение во вращении между двумя объектами:
        class RotaryLimitJoint(BaseConstraintObject):
            def __init__(self, a, b, min: float = -180, max: float = 180) -> None:
                self.constraint = pymunk.RotaryLimitJoint(a.body, b.body, -math.radians(min), -math.radians(max))
                a.body.space.add(self.constraint)

        # Создать храповое соединение между двумя объектами:
        class RatchetJoint(BaseConstraintObject):
            def __init__(self, a, b, phase: float = -180, ratchet: float = 180) -> None:
                self.constraint = pymunk.RatchetJoint(a.body, b.body, -math.radians(phase), -math.radians(ratchet))
                a.body.space.add(self.constraint)

        # Создать шестерёнестое соединение между двумя объектами:
        class GearJoint(BaseConstraintObject):
            def __init__(self, a, b, phase: float = -180, ratio: float = 180) -> None:
                self.constraint = pymunk.GearJoint(a.body, b.body, -math.radians(phase), -math.radians(ratio))
                a.body.space.add(self.constraint)

        # Создать двигательное соединение между двумя объектами:
        class SimpleMotor(BaseConstraintObject):
            def __init__(self, a, b, rpm=60.0) -> None:
                self.constraint = pymunk.SimpleMotor(a.body, b.body, -((math.radians(360)*2)/60)*rpm)
                a.body.space.add(self.constraint)

    # Класс пространства:
    class Space2D:
        def __init__(self, gravity: tuple, physics_speed: float = 1.0, damping: float = 1.0, iterations: int = 50,
                     idle_speed_threshold: float = 0.0, sleep_time_threshold: float = float("inf"),
                     collision_slop: float = 0.1, collision_bias: float = ((1-.5)**60)) -> None:
            """ Что означают параметры:
                gravity              - Мировая гравитация.
                physics_speed        - Скорость симуляции физики.
                damping              - Каждое тело будет терять % своей скорости в сек. Пример: 0.75 = 25%
                iterations           - Кол-во итераций точности физики. Влияет на производительность (сильно).
                idle_speed_threshold - Если скорость объекта меньше чем указано, он считается неподвижным.
                sleep_time_threshold - Если объект "неподвижный" в течении этого времени, он засыпает.
                collision_slop       - Допустимая степень перекрытия между фигурами.
                collision_bias       - Насколько быстро раздвигаются перекрывающиеся фигуры.
                                       Формула ((1 - 0.25)**60)) исправляет 25% ошибок каждые 1/60 секунды.
            """

            self.space                      = pymunk.Space()
            self.space.gravity              = gravity
            self.space.damping              = damping
            self.space.iterations           = iterations
            self.space.idle_speed_threshold = idle_speed_threshold
            self.space.sleep_time_threshold = sleep_time_threshold
            self.space.collision_slop       = collision_slop
            self.space.collision_bias       = collision_bias
            self.physics_speed              = abs(physics_speed)
            self.objects                    = []  # Все объекты в физическом пространстве.

        # Шаг симуляции:
        def step(self, delta_time: float) -> None:
            self.space.step(delta_time)

        # Обновление физики:
        def update(self, delta_time: float) -> None:
            self.physics_speed = abs(self.physics_speed)  # Нельзя допустить чтобы скорость физики была в минусе.

            # Корректировка дельты времени:
            fps = 30             # Пороговый фпс после которого начинаем урезать скорость симуляции.
            cut = delta_time*60  # Насколько урезать скорость симуляции (на 2 если 30 фпс, на 4 если 15 фпс и тд).
            delta_time = abs(1/fps/cut if delta_time > 1/fps else delta_time)

            # Проводим симуляцию:
            steps_count = max(1, int(self.physics_speed))
            step_time = (delta_time*self.physics_speed)/steps_count
            for _ in range(steps_count): self.step(step_time)

        # Добавить новый объект в пространство:
        def add(self, object: any) -> None:
            if type(object) is list:
                for obj in object:
                    if type(obj) is PyMunk.Objects.Mesh: self.space.add(obj.body, *obj.shapes)
                    elif obj.body is None: continue
                    elif obj.shape is None: self.space.add(obj.body)
                    else: self.space.add(obj.body, obj.shape)
                    self.objects.append(obj)
                return
            if type(object) is PyMunk.Objects.Mesh: self.space.add(object.body, *object.shapes)
            elif object.body is None: return
            elif object.shape is None: self.space.add(object.body)
            else: self.space.add(object.body, object.shape)
            self.objects.append(object)

        # Удалить объект из пространства:
        def remove(self, object: any) -> None:
            if type(object) is list:
                for obj in object:
                    if type(obj) is PyMunk.Objects.Mesh: self.space.remove(obj.body, *obj.shapes)
                    elif obj.body is None: continue
                    elif obj.shape is None: self.space.remove(obj.body)
                    else: self.space.remove(obj.body, obj.shape)
                    self.objects.remove(obj)
                return
            if type(object) is PyMunk.Objects.Mesh: self.space.remove(object.body, *object.shapes)
            elif object.body is None: return
            elif object.shape is None: self.space.remove(object.body)
            else: self.space.remove(object.body, object.shape)
            self.objects.remove(object)

        @property
        def gravity(self) -> list: return self.space.gravity

        @property
        def arbiters(self) -> list: return self.space.arbiters

        @property
        def collision_slop(self) -> float: return self.space.collision_slop

        @property
        def collision_bias(self) -> float: return self.space.collision_bias
