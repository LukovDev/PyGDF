#
# particles.py - Создаёт класс частиц.
#


# Импортируем:
if True:
    from .batch import SpriteBatch
    from .camera import Camera2D
    from .texture import Texture
    from ..math import *
    from ..utils import *


# Класс 2D частиц:
class ParticleEffect2D:
    """ Пример использования:
    particles = ParticleEffect2D(
        texture      = particle_texture,
        position     = vec2(0, 0),
        direction    = vec2(0, 0),
        size         = vec2(1, 1),
        speed        = vec2(1, 3),
        damping      = 0.01,
        duration     = vec2(1, 2),
        count        = 128,
        gravity      = vec2(0, 0),
        is_infinite  = False,
        is_local_pos = False,
        is_dir_angle = False,
        angle_offset = 0.0
    ).create()
    """

    # Частица:
    class Particle:
        def __init__(self,
                     texture:   Texture | list,
                     position:  vec2,
                     direction: vec2,
                     size:      vec2,
                     speed:     float,
                     time:      float
                     ) -> None:
            self.texture   = texture
            self.position  = position
            self.direction = direction
            self.size      = size
            self.speed     = speed
            self.time      = time

    # Инициализация:
    def __init__(self,
                 texture:      Texture | list,
                 position:     vec2,
                 direction:    vec2,
                 size:         vec2,
                 speed:        vec2,
                 damping:      float,
                 duration:     vec2,
                 count:        int,
                 gravity:      vec2,
                 is_infinite:  bool  = True,
                 is_local_pos: bool  = False,
                 is_dir_angle: bool  = True,
                 angle_offset: float = 0.0
                 ) -> None:
        # Внутренние переменные класса:
        self.batch       = SpriteBatch()  # Пакетная отрисовка.
        self.__old_pos__ = position       # Старая позиция
        self.__timer__   = 0.0            # Счётчик отсчитывающий время для создания новой частицы.
        self.particles   = None           # Список частиц.

        # Параметры отображения:
        self.texture      = texture       # Текстура частиц.
        self.is_dir_angle = is_dir_angle  # Поворачивать ли частицу в сторону направления движения.
        self.angle_offset = angle_offset  # Смещения угла поворота частицы.

        # Параметры частиц:
        self.position     = position      # Позиция эффекта частиц.
        self.direction    = direction     # Вектор направления частиц.
        self.size         = size          # Размер частиц.
        self.speed        = speed         # Начальная скорость частицы. Случайно от X до Y.
        self.damping      = damping       # Сила затухания скорости частицы.
        self.duration     = duration      # Сколько должна жить частица (в секундах). Случайно от X до Y.

        # Прочие параметры:
        self.count        = count         # Количество частиц.
        self.gravity      = gravity       # Сила гравитации на частицы.
        self.is_infinite  = is_infinite   # Бесконечные ли частицы.
        self.is_local_pos = is_local_pos  # Частицы в локальном пространстве.

    # Создать одну частицу. Используется строго внутри этого класса:
    def __create_particle__(self) -> None:
        random_dir = vec2(random.uniform(-1.0, +1.0), random.uniform(-1.0, +1.0))  # Случайное направление.
        direction = self.direction.y, -self.direction.x  # Повёрнутый на 90 градусов, вектор направления.

        ptxt = self.texture if type(self.texture) is Texture else random.choice(self.texture)
        ppos = self.position.xy
        pdir = normalize(random_dir + direction)
        psiz = self.size.xy
        pspd = random.uniform(*self.speed.xy)
        ptfl = random.uniform(*self.duration.xy)

        # Частица:
        particle = ParticleEffect2D.Particle(
            ptxt,  # Текстура частицы.
            ppos,  # Позиция.
            pdir,  # Вектор скорости.
            psiz,  # Размер.
            pspd,  # Скорость.
            ptfl   # Время жизни частицы.
        )

        # Добавляем частицу к другим частицам:
        self.particles.append(particle)

    # Создать эффект частиц:
    def create(self) -> "ParticleEffect2D":
        self.particles = []

        for i in range(0 if self.is_infinite else self.count):
            self.__create_particle__()

        return self

    # Обновление частиц:
    def update(self, delta_time: float) -> "ParticleEffect2D":
        delta_time = delta_time * 60
        gravity    = vec2(self.gravity.y, -self.gravity.x)

        # Урезаем лишние частицы:
        self.particles = self.particles[:self.count]

        # Если количество частиц меньше установленного, создаём новые:
        if len(self.particles) < self.count and self.is_infinite:
            self.__timer__ -= 1.0 / 60 * delta_time
            if self.__timer__ <= 0.0:
                self.__timer__ = 1/(self.count/max(self.duration))
                self.__create_particle__()

        # Проходимся по частицам:
        for particle in self.particles:
            # Время жизни частицы. Если время вышло, удаляем частицу:
            particle.time -= 1.0 / 60 * delta_time
            if particle.time <= 0.0:
                self.particles.remove(particle)
                if self.is_infinite: self.__create_particle__()
                continue  # Пропускаем итерацию.

            # Применяем гравитацию к направлению частицы:
            particle.direction += gravity * self.damping * delta_time
                        
            # Применяем гравитацию к скорости частицы:
            # TODO: Мне не нравится эта реализация. Надо будет как нибуть потом переделать.
            if length(gravity) > 0:
                speed = length(gravity * delta_time) * self.damping
                if dot(particle.direction, gravity) < 0: particle.speed -= speed
                else: particle.speed += speed
            else: particle.speed += -(self.damping * particle.speed) * delta_time

            # Перемещаем частичку в сторону её направления на расстояние равной её скорости:
            particle.position += get_delta_pos_vector_2d(particle.direction, particle.speed * delta_time)
            if self.is_local_pos: particle.position += self.position - self.__old_pos__

        self.__old_pos__ = self.position
        return self

    # Отрисовка частиц:
    def render(self) -> "ParticleEffect2D":
        self.batch.begin()

        # Проходимся по частицам:
        for particle in self.particles:
            # Получаем сокращённые параметры:
            ptxt = particle.texture
            ppos = particle.position
            pdir = particle.direction
            psiz = particle.size
            angl = get_angle_points_2d((0, 0), pdir.xy) if self.is_dir_angle else 0.0

            # Рисуем частицу:
            self.batch.draw(
                sprite = ptxt,
                x      = ppos.x - (psiz.x/2),
                y      = ppos.y - (psiz.y/2),
                width  = psiz.x,
                height = psiz.y,
                angle  = angl + self.angle_offset
            )

        self.batch.end()
        return self

    # Удалить систему частиц:
    def destroy(self) -> None:
        if self.texture is None: return
        self.texture.destroy()
