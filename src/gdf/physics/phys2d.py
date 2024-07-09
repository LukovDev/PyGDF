#
# phys2d.py - Создаёт реализацию 2D физики.
#


# Импортируем:
if True:
    import pymunk
    from ..math import *


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
                self.mass        = mass         # Масса объекта.
                self.elasticity  = elasticity   # Сила упругости.
                self.friction    = friction     # Сила трения.
                self.body_type   = body_type    # Тип объекта.
                self.max_vel     = max_vel      # Максимальная скорость перемещения.
                self.max_ang_vel = max_ang_vel  # Максимальная скорость вращения.
                self.space       = None         # Физическое пространство.
                self.body        = None         # Тело объекта.
                self.shape       = None         # Форма объекта.
                self.kgn         = 9.80665      # Константа для перевода сил из ньютонов в килограммы.

            @property
            def position(self) -> vec2: return vec2(self.body.position)

            @property
            def angle(self) -> float: return -degrees(self.body.angle)

            @property
            def velocity(self) -> vec2: return vec2(self.body.velocity)

            @property
            def angular_velocity(self) -> float: return self.body.angular_velocity

            @property
            def constraints(self) -> list: return list(self.body.constraints)

            # Новая функция для получения списка тел, с которыми данное тело сталкивается
            @property
            def collisions(self) -> list:
                if self.space is None:
                    raise PhysicsError("You have not added a physical object to the space.")
                colliding_bodies = []
                for arbiter in self.space.arbiters:
                    if   arbiter.shapes[0].body == self.body: colliding_bodies.append(arbiter.shapes[1].body)
                    elif arbiter.shapes[1].body == self.body: colliding_bodies.append(arbiter.shapes[0].body)
                return colliding_bodies

            # Установить позицию телу:
            def set_position(self, position: vec2) -> None:
                self.body.position = tuple(position)

            # Установить угол наклона телу:
            def set_angle(self, angle: float) -> None:
                self.body.angle = radians(-angle)

            # Применить силу к этому телу:
            def apply_local_force(self, force: vec2, point: vec2 = vec2(0)) -> None:
                self.body.apply_force_at_local_point(tuple(force.xy*self.kgn), point)

            # Применить силу к этому телу в мировых координатах:
            def apply_global_force(self, force: vec2, point: vec2 = vec2(0)) -> None:
                self.body.apply_force_at_world_point(tuple(force.xy*self.kgn), point)

            # Применить импульс к этому телу:
            def apply_local_impulse(self, impulse: vec2, point: vec2 = vec2(0)) -> None:
                self.body.apply_impulse_at_local_point(tuple(impulse.xy*self.kgn), point)

            # Применить импульс к этому телу в мировых координатах:
            def apply_global_impulse(self, impulse: vec2, point: vec2 = vec2(0)) -> None:
                self.body.apply_impulse_at_world_point(tuple(impulse.xy*self.kgn), point)

            # Установить крутящий момент:
            def set_torque(self, torque: float) -> None:
                self.body.angular_velocity = -radians(torque)

            # Функция ограничения скорости вращения и перемещения:
            def __limit_velocity_func__(self) -> any:
                def limit_velocity(body, gravity, damping, dt) -> None:
                    pymunk.Body.update_velocity(body, gravity, damping, dt)
                    if body.velocity.length > self.max_vel:
                        body.velocity *= (self.max_vel / body.velocity.length)
                    if abs(body.angular_velocity) > self.max_ang_vel:
                        if body.angular_velocity < 0: body.angular_velocity = radians(self.max_ang_vel)
                        else: body.angular_velocity = -radians(self.max_ang_vel)
                return limit_velocity

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
                self.size             = vec2(abs(size.x), abs(size.y))
                self.body             = pymunk.Body(mass, pymunk.moment_for_box(mass, size), body_type)
                self.body.position    = tuple(position.xy)
                self.body.angle       = radians(angle)
                self.shape            = pymunk.Poly.create_box(self.body, size)
                self.shape.elasticity = self.elasticity
                self.shape.friction   = self.friction
                self.body.velocity_func = self.__limit_velocity_func__()

            @property
            def vertices(self) -> list: return self.shape.get_vertices()

    # Пространство симуляции:
    class Space:
        def __init__(self,
                     gravity:        vec2,
                     phys_speed:     float = 1.0,
                     meter:          float = 100.0,
                     damping:        float = 1.0,
                     iterations:     int   = 64,
                     idle_speed:     float = 0.0,
                     sleep_time:     float = float("inf"),
                     collision_slop: float = 0.1,
                     collision_bias: float = ((1-.5)**60)
                     ) -> None:
            self.space                      = pymunk.Space()           # Физическое пространство.
            self.phys_speed                 = abs(phys_speed)          # Скорость симуляции физики.
            self.space.gravity              = tuple(gravity.xy*meter)  # Сила гравитации.
            self.space.damping              = damping                  # Сила трения об воздух.
            self.space.iterations           = iterations               # Количество итераций столкновений за шаг.
            self.space.idle_speed_threshold = idle_speed               # Порог скорости объекта, после чего он статичен.
            self.space.sleep_time_threshold = sleep_time               # Время спокойствия объекта после чего он спящий.
            self.space.collision_slop       = collision_slop*meter     # Допустимое пересечение при столкновении.
            self.space.collision_bias       = collision_bias*meter     # Смещение при столкновении объектов.
            self.objects                    = []                       # Список всех физических объектов.

        # Шаг симуляции:
        def step(self, delta_time: float) -> None:
            self.space.step(delta_time)

        # Обновление физики:
        def update(self, delta_time: float) -> None:
            # Нельзя допустить чтобы скорость физики была в минусе:
            self.phys_speed = abs(self.phys_speed)

            # Шаг симуляции:
            self.step(delta_time*self.phys_speed)

            # Корректировка дельты времени:
            # fps = 30             # Пороговый фпс после которого начинаем урезать скорость симуляции.
            # cut = delta_time*60  # Насколько урезать скорость симуляции (на 2 если 30 фпс, на 4 если 15 фпс и тд).
            # delta_time = abs(1/fps/cut if delta_time > 1/fps else delta_time)

            # # Проводим симуляцию:
            # steps_count = int(max(1, int(self.physics_speed)))
            # step_time = (delta_time*self.physics_speed)/steps_count
            # for _ in range(steps_count): self.step(step_time)

        # Добавить новый объект в пространство:
        def add(self, object: "Physics2D.Objects") -> None:
            object = [object] if not isinstance(object, list) else object
            for obj in object:
                # if isinstance(obj, Objects.Mesh): self.space.add(obj.body, *obj.shapes)
                if obj.body is None: continue
                elif obj.shape is None: self.space.add(obj.body)
                else: self.space.add(obj.body, obj.shape)
                self.objects.append(obj)

        # Удалить объект из пространства:
        def remove(self, object: "Physics2D.Objects") -> None:
            object = [object] if not isinstance(object, list) else object
            for obj in object:
                # if isinstance(obj, Objects.Mesh): self.space.remove(obj.body, *obj.shapes)
                if obj.body is None: continue
                elif obj.shape is None: self.space.remove(obj.body)
                else: self.space.remove(obj.body, obj.shape)
                self.objects.remove(obj)

        @property
        def gravity(self) -> list: return self.space.gravity

        @property
        def arbiters(self) -> list: return self.space.arbiters

        @property
        def collision_slop(self) -> float: return self.space.collision_slop

        @property
        def collision_bias(self) -> float: return self.space.collision_bias
