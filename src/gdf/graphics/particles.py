#
# particles.py - Создаёт класс частиц.
#


# Импортируем:
from .batch import SpriteBatch2D
from .texture import Texture
from ..math import *
from ..utils import Utils2D


# Класс 2D частиц:
class ParticleEffect2D:
    """ Пример использования:
        particles = ParticleEffect2D(
            texture       = [particle_texture],
            position      = vec2(0, 0),
            direction     = vec2(0, 0),
            start_size    = [vec2(16, 16), vec2(16, 16)],
            end_size      = [vec2(0, 0), vec2(0, 0)],
            speed         = vec2(3, 10),
            damping       = 0.01,
            duration      = vec2(1, 2),
            count         = 512,
            gravity       = vec2(0, 0),
            start_angle   = vec2(0.0),
            end_angle     = vec2(0.0),
            size_exp      = 1.0,
            angle_exp     = 1.0,
            is_infinite   = False,
            is_local_pos  = False,
            is_dir_angle  = False,
            spawn_in      = ParticleEffect2D.SpawnInPoint(),
            custom_update = None
        ).create()
    """

    """ Пример кастомной функции обновления частиц:
        def custom_update(delta_time: float, particles: list) -> None:
            for particle in list(particles):
                particle.position.xy += particle.velocity.xy * delta_time
    """

    # Создать частицу в точке:
    class SpawnInPoint:
        def __init__(self) -> None:
            pass

        # Получить позицию частицы:
        def get_position(self) -> vec2:
            return vec2(0.0)

        # Получить направление частицы:
        def get_direction(self, orig_pos: vec2, spawn_pos: vec2) -> vec2:
            a = random.uniform(0, 2*math.pi)
            return vec2(sin(a), cos(a))

    # Создать частицу в круге:
    class SpawnInCircle:
        def __init__(self, radius: float, dir_out: bool = True) -> None:
            self.radius  = radius
            self.dir_out = dir_out

        # Получить позицию частицы:
        def get_position(self) -> vec2:
            a = random.uniform(0, 2*math.pi)
            d = vec2(sin(a), cos(a))
            return d * (self.radius*random.uniform(0, 1))

        # Получить направление частицы:
        def get_direction(self, orig_pos: vec2, spawn_pos: vec2) -> vec2:
            if self.dir_out: return normalize(spawn_pos.xy-orig_pos.xy)
            else:
                a = random.uniform(0, 2*math.pi)
                return vec2(sin(a), cos(a))

    # Создать частицу в прямоугольнике:
    class SpawnInSquare:
        def __init__(self, size: vec2, angle: float = 0.0, dir_out: bool = False) -> None:
            self.size    = size
            self.angle   = angle
            self.dir_out = dir_out

        # Получить позицию частицы:
        def get_position(self) -> vec2:
            x = random.uniform(-self.size.x/2, +self.size.x/2)
            y = random.uniform(-self.size.y/2, +self.size.y/2)
            if self.angle == 0.0: return vec2(x, y)  # Если угол равен нулю, возвращаем обычные координаты.

            ca, sa = math.cos(-self.angle), math.sin(-self.angle)
            rx, ry = x*ca - y*sa, x*sa + y*ca  # Вращаем координату.
            return vec2(rx, ry)

        # Получить направление частицы:
        def get_direction(self, orig_pos: vec2, spawn_pos: vec2) -> vec2:
            if self.dir_out: return normalize(spawn_pos.xy-orig_pos.xy)
            else:
                a = random.uniform(0, 2*math.pi)
                return vec2(sin(a), cos(a))

    # Создать частицу в линии:
    class SpawnInLine:
        def __init__(self, point1: vec2, point2: vec2) -> None:
            self.point1 = point1
            self.point2 = point2

        # Получить позицию частицы:
        def get_position(self) -> vec2:
            r = random.uniform(0, 1)  # Значение от 0.0 до 1.0 для интерполяции.
            return vec2(
                self.point1.x+r*(self.point2.x-self.point1.x),
                self.point1.y+r*(self.point2.y-self.point1.y)
            )

        # Получить направление частицы:
        def get_direction(self, orig_pos: vec2, spawn_pos: vec2) -> vec2:
            a = random.uniform(0, 2*math.pi)
            return vec2(sin(a), cos(a))

    # Частица:
    class Particle:
        def __init__(self,
                     texture:   Texture | list,
                     position:  vec2,
                     velocity:  vec2,
                     angle:     float,
                     end_angle: float,
                     size:      vec2,
                     end_size:  vec2,
                     time:      float
                     ) -> None:
            self.texture    = texture
            self.position   = position
            self.velocity   = velocity
            self.angle      = angle
            self.s_angle    = angle
            self.e_angle    = end_angle
            self.size       = size.xy
            self.s_size     = size.xy
            self.e_size     = end_size.xy
            self.time       = time
            self.start_time = time

        # Скорость перемещения частицы:
        @property
        def speed(self) -> float: return Utils2D.get_speed_vector(self.velocity)

    # Инициализация:
    def __init__(self,
                 texture:       Texture | list,
                 position:      vec2,
                 direction:     vec2,
                 start_size:    vec2 | list[vec2],
                 end_size:      vec2 | list[vec2],
                 speed:         vec2,
                 damping:       float,
                 duration:      vec2,
                 count:         int,
                 gravity:       vec2,
                 start_angle:   float | vec2 = vec2(0.0),
                 end_angle:     float | vec2 = vec2(0.0),
                 size_exp:      float = 1.0,
                 angle_exp:     float = 1.0,
                 is_infinite:   bool  = True,
                 is_local_pos:  bool  = False,
                 is_dir_angle:  bool  = True,
                 spawn_in:      SpawnInPoint | SpawnInCircle | SpawnInSquare | SpawnInLine = None,
                 custom_update: any = None
                 ) -> None:
        # Подготовка данных:

        # Подготовка начальных и конечных размеров частиц:
        if not isinstance(start_size, list):      # Если это не массив из двух векторов, делаем его массивом.
            if not isinstance(start_size, vec2):  # Если это даже не вектор, делаем его вектором.
                start_size = vec2(start_size)
            start_size = [start_size, start_size]
        if not isinstance(end_size, list):      # Если это не массив из двух векторов, делаем его массивом.
            if not isinstance(end_size, vec2):  # Если это даже не вектор, делаем его вектором.
                end_size = vec2(end_size)
            end_size = [end_size, end_size]

        # Подготовка продолжительности жизни частицы:
        duration, speed = vec2(duration), vec2(speed)

        # Подготовка начальных и конечных углов частиц:
        start_angle, end_angle = vec2(start_angle), vec2(end_angle)

        # Параметры:
        self.texture       = texture        # Текстура частиц.
        self.position      = position       # Позиция эффекта частиц.
        self.direction     = direction      # Вектор направления частиц.
        self.start_size    = start_size     # Начальный размер частиц (два вектора между которыми выбирается случ.разм).
        self.end_size      = end_size       # Конечный размер частиц (два вектора между которыми выбирается случ.разм).
        self.speed         = speed          # Начальная скорость частицы. Случайно от X до Y.
        self.damping       = damping        # Сила затухания скорости частицы.
        self.duration      = duration       # Сколько должна жить частица (в секундах). Случайно от X до Y.
        self.count         = count          # Количество частиц.
        self.gravity       = gravity        # Сила гравитации.
        self.start_angle   = start_angle    # Начальный угол частицы (2 значения между которыми выбирается случ.число).
        self.end_angle     = end_angle      # Конечный угол частицы (2 значения между которыми выбирается случ.число).
        self.size_exp      = size_exp       # Экспоненциальное масштабирование размера.
        self.angle_exp     = angle_exp      # Экспоненциальный поворот.
        self.is_infinite   = is_infinite    # Бесконечные ли частицы.
        self.is_local_pos  = is_local_pos   # Частицы в локальном пространстве.
        self.is_dir_angle  = is_dir_angle   # Поворачивать ли частицу в сторону направления движения.
        self.spawn_in      = spawn_in       # Как создавать частицу (укажите класс спавнера частиц).
        self.custom_update = custom_update  # Кастомный обновлятор частиц.

        # Если передали пустой спавнер, создаём спавнер по умолчанию (точка):
        if self.spawn_in is None: self.spawn_in = ParticleEffect2D.SpawnInPoint()

        # Внутренние переменные класса:
        self.particles = None  # Список частиц.
        self._partvars_ = {
            "batch":   SpriteBatch2D(),
            "old-pos": position.xy,
            "timer":   0.0,
            "old-dt":  1/60,
        }

    # Создать одну частицу. Используется строго внутри этого класса:
    def _create_particle_(self) -> None:
        spwn_pos = self.spawn_in.get_position()
        spwn_dir = self.spawn_in.get_direction(self.position, spwn_pos)

        ptxt = self.texture if type(self.texture) is Texture else random.choice(self.texture)
        ppos = self.position.xy + spwn_pos.xy
        pvel = normalize(spwn_dir+self.direction) * random.uniform(*self.speed.xy)

        pang = random.uniform(*self.start_angle.xy)
        peag = random.uniform(*self.end_angle.xy)

        psiz = vec2(
            random.uniform(self.start_size[0].x, self.start_size[1].x),
            random.uniform(self.start_size[0].y, self.start_size[1].y)
        )
        pnsz = vec2(
            random.uniform(self.end_size[0].x, self.end_size[1].x),
            random.uniform(self.end_size[0].y, self.end_size[1].y)
        )

        ptfl = random.uniform(*self.duration.xy)

        # Частица:
        particle = ParticleEffect2D.Particle(
            ptxt,  # Текстура частицы.
            ppos,  # Позиция.
            pvel,  # Вектор направления и скорости.
            pang,  # Угол поворота.
            peag,  # Конечный угол поворота.
            psiz,  # Размер.
            pnsz,  # Конечный размер.
            ptfl   # Время жизни частицы.
        )

        # Добавляем частицу к другим частицам:
        self.particles.append(particle)

    # Создать эффект частиц:
    def create(self) -> "ParticleEffect2D":
        if self.particles is None: self.particles = []

        for i in range(0 if self.is_infinite else self.count-len(self.particles)):
            self._create_particle_()

        return self

    # Обновление частиц:
    def update(self, delta_time: float) -> "ParticleEffect2D":
        if self.particles is None: return

        if self.custom_update is not None: self.custom_update(delta_time, self.particles) ; return

        # Если новый dt больше старого в 2 раза, то используем старый dt. А также ограничиваем dt до 1/10 кадра в сек:
        dt = min(self._partvars_["old-dt"] if delta_time > self._partvars_["old-dt"] * 2 else delta_time, 1/10)
        self._partvars_["old-dt"] = delta_time

        # Если количество частиц меньше установленного, создаём новые:
        if len(self.particles) < self.count and self.is_infinite:
            self._partvars_["timer"] -= dt
            while self._partvars_["timer"] <= 0.0:
                self._create_particle_()
                self._partvars_["timer"] += (sum(self.duration) / 2) / self.count

        # Урезаем лишние частицы (на всякий случай ограничиваем их количество):
        self.particles = self.particles[:self.count]

        # Проходимся по частицам (проходимся по последней копии списка частиц):
        for particle in list(self.particles):
            # Уменьшаем время жизни частицы:
            particle.time -= dt

            # Применяем гравитацию к направлению частицы:
            particle.velocity += self.gravity * dt
            particle.velocity *= 1.0 - self.damping

            # Перемещаем частичку в сторону её направления умноженное на её скорость:
            particle.position += normalize(particle.velocity) * particle.speed * dt
            if self.is_local_pos: particle.position += self.position - self._partvars_["old-pos"]

            # Прогресс жизни частицы от 0 до 1:
            prgss = 1.0 - (particle.time / particle.start_time)

            # Вращаем частицу:
            if particle.s_angle != particle.e_angle:  # Только если начальный и конечный не одинаковы:
                particle.angle = mix(particle.s_angle, particle.e_angle, smoothstep(0, 1, prgss**self.angle_exp))

            # Меняем размер:
            if particle.s_size.xy != particle.e_size.xy:  # Только если начальный и конечный не одинаковы:
                particle.size.xy = mix(particle.s_size.xy, particle.e_size.xy, smoothstep(0, 1, prgss**self.size_exp))

            # Удаляем частицу только после всех изменений и если её время вышло:
            if particle.time <= 0.0:
                self.particles.remove(particle)
                if self.is_infinite: self._create_particle_()

        self._partvars_["old-pos"].xy = self.position.xy
        return self

    # Отрисовка частиц:
    def render(self, color: list = None, batch: SpriteBatch2D = None) -> "ParticleEffect2D":
        if self.particles is None: return

        # Проходимся по частицам:
        if batch is None: self._partvars_["batch"].begin()
        for particle in self.particles:
            angl = Utils2D.get_angle_points(vec2(0), normalize(particle.velocity)) + 90 if self.is_dir_angle else 0.0

            # Рисуем частицу:
            sprite_batch = self._partvars_["batch"] if batch is None else batch
            sprite_batch.draw(
                particle.texture,
                particle.position.x - particle.size.x / 2,
                particle.position.y - particle.size.y / 2,
                particle.size.x,
                particle.size.y,
                angl + particle.angle
            )
        if batch is None:
            self._partvars_["batch"].end()
            self._partvars_["batch"].render(color)
        return self

    # Удалить систему частиц:
    def destroy(self) -> None:
        if self.texture is None: return
        self.texture.destroy()
