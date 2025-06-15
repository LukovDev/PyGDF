#
# controllers.py - Создаёт классы-контроллеры камеры. Чтобы можно было свободно перемещаться по OpenGL пространству.
#


# Импортируем:
from .graphics import Camera2D, Camera3D
from .input import InputHandler, Key
from .math import *


# Проверяем и перемещаем курсор мыши если тот рядом с границей окна:
def check_mouse_pos(input, camera, x_pos_detect: int = 16, y_pos_detect: int = 16) -> None:
    mouse_pos = input.get_mouse_pos()
    set_mouse = input.set_mouse_pos
    win_size  = camera.width, camera.height
    if mouse_pos[0] < x_pos_detect:               set_mouse((win_size[0] - x_pos_detect, mouse_pos[1]))
    if mouse_pos[0] > win_size[0] - x_pos_detect: set_mouse((x_pos_detect, mouse_pos[1]))
    if mouse_pos[1] < y_pos_detect:               set_mouse((mouse_pos[0], win_size[1] - y_pos_detect))
    if mouse_pos[1] > win_size[1] - y_pos_detect: set_mouse((mouse_pos[0], y_pos_detect))


# Класс управления 2D камеры:
class CameraController2D:
    def __init__(self, input: InputHandler, camera: Camera2D,
                 offset_scale: float = 1.0,
                 min_zoom:     float = 1/1000,
                 max_zoom:     float = 128000,
                 friction:     float = 0.2) -> None:
        self.input  = input
        self.camera = camera

        self.fixed_mouse_pos = (0, 0)
        self.offset_scale = offset_scale
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.friction = friction
        self.target_pos = vec2(self.camera.position.xy)

    # Обновление камеры:
    def update(self, delta_time: float, pressed_pass: bool = False) -> None:
        mouse_pressed = self.input.get_mouse_pressed()
        mouse_scroll  = self.input.get_mouse_scroll()
        mouse_pos     = self.input.get_mouse_pos()
        mouse_rel     = self.input.get_mouse_rel()
        is_zooming    = not pressed_pass or mouse_pressed[0]

        # Если нажимают на колёсико мыши:
        if mouse_pressed[1]:
            meter, zoom = self.camera.meter, self.camera.zoom
            delta_pos = mouse_pos[0] - self.fixed_mouse_pos[0], mouse_pos[1] - self.fixed_mouse_pos[1]
            self.target_pos.x += ((delta_pos[0]*1/(250*5))*self.offset_scale*zoom*meter)*(delta_time*60)
            self.target_pos.y -= ((delta_pos[1]*1/(250*5))*self.offset_scale*zoom*meter)*(delta_time*60)

        # Если нажимают на пкм (правую кнопку мыши):
        elif mouse_pressed[2]:
            is_zooming = True
            self.camera.position.x -= (mouse_rel[0] * self.camera.zoom) * self.camera.meter / 100
            self.camera.position.y += (mouse_rel[1] * self.camera.zoom) * self.camera.meter / 100
            self.target_pos = self.camera.position.xy
            check_mouse_pos(self.input, self.camera, 16, 16)
            self.fixed_mouse_pos = mouse_pos
        else: self.fixed_mouse_pos = mouse_pos

        meter = self.camera.meter
        if is_zooming: self.camera.zoom -= mouse_scroll[1] * self.camera.zoom * 0.1
        if self.camera.zoom*meter < self.min_zoom: self.camera.zoom = self.min_zoom*1/meter
        if self.camera.zoom       > self.max_zoom: self.camera.zoom = self.max_zoom

        self.camera.position.x += ((self.target_pos.x-self.camera.position.x)*self.friction)*(delta_time*60)
        self.camera.position.y += ((self.target_pos.y-self.camera.position.y)*self.friction)*(delta_time*60)


# Класс управления 3D камеры:
class CameraController3D:
    def __init__(self, input: InputHandler, camera: Camera3D,
                 mouse_sensitivity: float = 1.0,
                 ctrl_speed:        float = 0.75,
                 speed:             float = 6.0,
                 shift_speed:       float = 24.0,
                 friction:          float = 1.0,
                 up_is_forward:     bool  = False) -> None:
        self.input  = input
        self.camera = camera

        self.mouse_sensitivity = mouse_sensitivity
        self.ctrl_speed        = ctrl_speed
        self.speed             = speed
        self.shift_speed       = shift_speed
        self.friction          = friction
        self.up_is_forward     = up_is_forward

        self.up      = vec3(0, 1, 0)
        self.right   = vec3(1, 0, 0)
        self.forward = vec3(0, 0, 0)

        self.is_movement   = False
        self.camera_target = vec3(self.camera.position.xyz)

        self.pressed_pass = False
        self.is_pressed = False

    # Обновление контроллера:
    def update(self, delta_time: float, pressed_pass: bool = False) -> None:
        # Получаем нажатие кнопки мыши:
        mouse_pressed = self.input.get_mouse_pressed()[2]

        # Получаем смещение мыши:
        mouse_delta_xy = self.input.get_mouse_rel()

        # Eсли мы зажали ПКМ и не попали на интерфейс, то можем свободно управлять камерой пока не отпустим ПКМ:        
        if mouse_pressed and not pressed_pass and not self.is_pressed:
            self.is_pressed = True

        # Если мы попали на интерфейс когда зажали ПКМ, то управлять мы не можем:
        if mouse_pressed and pressed_pass and not self.is_pressed:
            self.pressed_pass = True

        # Если мы отпустили ПКМ, то всё сбрасываем:
        if not mouse_pressed:
            self.pressed_pass = False
            self.is_pressed = False

        # Управление камерой в случае если мы не попали на интерфейс и зажали ПКМ:
        if self.is_pressed and not self.pressed_pass:
            self.keyboard_control(delta_time)
            self.mouse_control(mouse_delta_xy)

        # Плавное перемещение:
        fr = 1-self.friction
        if fr > 0.0:
            self.camera.position += ((self.camera_target-self.camera.position)*1/fr) * delta_time
        else: self.camera.position = self.camera_target

        # Проверяем перемещается камера или нет:
        if round(glm.length(self.camera_target-self.camera.position), 4) > 0.001:
            self.is_movement = True
        else: self.is_movement = False

        # Если координаты камеры сломались, обнуляем их:
        if any([isnan(v) for v in self.camera_target.xyz]): self.camera_target = vec3(0)

    # Управление с помощью мыши:
    def mouse_control(self, mouse_delta_xy: tuple[int, int]) -> None:
        # Добавляем смещение мыши к рысканью и тангажу:
        self.camera.rotation.y += mouse_delta_xy[0] * (self.mouse_sensitivity * 0.1)  # По горизонтали.
        self.camera.rotation.x -= mouse_delta_xy[1] * (self.mouse_sensitivity * 0.1)  # По вертикали.
        check_mouse_pos(self.input, self.camera, 16, 16)  # Проверяем позицию мыши.

        # Если мы не перемещаемся вверх-вниз в зависимости от направления, ограничиваем взгляд по вертикали на 90 град.:
        if not self.up_is_forward: self.camera.rotation.x = clamp(self.camera.rotation.x, -90, +90)

    # Управление с помощью клавиатуры:
    def keyboard_control(self, delta_time: float) -> None:
        keys = self.input.get_key_pressed()

        # Если нажимают на левый или правый шифт, ускорить перемещение:
        if keys[Key.K_LSHIFT] or keys[Key.K_RSHIFT]:
            speed = self.shift_speed * delta_time
        # Иначе если нажимают CTRL:
        elif keys[Key.K_LCTRL] or keys[Key.K_RCTRL]:
            speed = self.ctrl_speed * delta_time
        else: speed = self.speed * delta_time

        # Углы камеры:
        pitch, yaw = radians(self.camera.rotation.x), -radians(self.camera.rotation.y)

        # Направления по осям:
        self.forward = normalize(vec3(cos(pitch) * sin(yaw), -sin(pitch), +cos(pitch) * cos(yaw)))
        self.right = normalize(cross(self.forward, vec3(0, 1, 0)))

        # Перемещать ли камеру вверх-вниз в зависимости от направления взгляда или нет:
        if self.up_is_forward: self.up = cross(-self.forward, self.right)
        else: self.forward = -normalize(cross(self.right, vec3(0, 1, 0)))

        # Управление движением:
        if keys[Key.K_w]: self.camera_target -= self.forward * speed
        if keys[Key.K_s]: self.camera_target += self.forward * speed
        if keys[Key.K_a]: self.camera_target += self.right * speed
        if keys[Key.K_d]: self.camera_target -= self.right * speed
        if keys[Key.K_q]: self.camera_target -= self.up * speed
        if keys[Key.K_e]: self.camera_target += self.up * speed

        # Вращать крен камеры:
        if keys[Key.K_LEFT]:  self.camera.rotation.z -= 25.0 * delta_time
        if keys[Key.K_RIGHT]: self.camera.rotation.z += 25.0 * delta_time


# Класс управления 3D орбитальной камеры:
class CameraOrbitController3D:
    def __init__(self, input: InputHandler, camera: Camera3D,
                 target_position:   vec3  = vec3(0, 0, 0),
                 distance:          float = 3.0,
                 mouse_sensitivity: float = 1.0,
                 friction:          float = 1.0,
                 up_is_forward:     bool  = False) -> None:
        self.input  = input
        self.camera = camera

        self.target_position   = target_position
        self.distance          = distance
        self.mouse_sensitivity = mouse_sensitivity
        self.friction          = friction
        self.up_is_forward     = up_is_forward

        self.up      = vec3(0, 1, 0)
        self.right   = vec3(1, 0, 0)
        self.forward = vec3(0, 0, 0)

        self.is_movement     = False
        self.rotate_target   = self.camera.rotation.xyz
        self.distance_target = float(distance)

        self.pressed_pass = False
        self.is_pressed   = False

    # Обновление контроллера:
    def update(self, delta_time: float, pressed_pass: bool = False) -> None:
        # Получаем нажатие кнопки мыши:
        mouse_pressed = self.input.get_mouse_pressed()[2]

        # Получаем смещение мыши:
        mouse_delta_xy = self.input.get_mouse_rel()

        # Eсли мы зажали ПКМ и не попали на интерфейс, то можем свободно управлять камерой пока не отпустим ПКМ:        
        if mouse_pressed and not pressed_pass and not self.is_pressed:
            self.is_pressed = True

        # Если мы попали на интерфейс когда зажали ПКМ, то управлять мы не можем:
        if mouse_pressed and pressed_pass and not self.is_pressed:
            self.pressed_pass = True

        # Если мы отпустили ПКМ, то всё сбрасываем:
        if not mouse_pressed:
            self.pressed_pass = False
            self.is_pressed = False

        # Управление камерой в случае если мы не попали на интерфейс и зажали ПКМ:
        if self.is_pressed and not self.pressed_pass:
            self.keyboard_control(delta_time)
            self.mouse_control(mouse_delta_xy)

        # Если мы не попали на интерфейс:
        if not pressed_pass:
            # Масштабируем расстояние:
            self.distance_target -= self.input.get_mouse_scroll()[1] * self.distance_target * 0.1

        # Плавное масштабирование расстояния и перемещение:
        fr = 1-self.friction
        if fr > 0.0:
            self.distance += ((self.distance_target-self.distance)*1/fr) * delta_time
            self.rotate_target += ((self.camera.rotation-self.rotate_target)*1/fr) * delta_time
        else:
            self.distance = self.distance_target
            self.rotate_target.xyz = self.camera.rotation.xyz

        # Вычисляем позицию камеры:
        pitch, yaw = -radians(self.rotate_target.x), -radians(self.rotate_target.y)
        self.forward = normalize(vec3(cos(pitch) * sin(yaw), sin(pitch), cos(pitch) * cos(yaw)))
        self.camera.position = self.target_position+self.forward*self.distance

        # Проверяем перемещается камера или нет (проверка по вращению и масштабированию):
        if round(glm.length(self.camera.rotation-self.rotate_target), 4) > 0.001 or \
           round(glm.length(self.distance_target-self.distance), 4) > 0.001:
            self.is_movement = True
        else: self.is_movement = False

        # Если координаты камеры сломались, обнуляем их:
        if any([isnan(v) for v in self.camera.position.xyz]): self.camera.position = vec3(0)

    # Управление с помощью мыши:
    def mouse_control(self, mouse_delta_xy: tuple[int, int]) -> None:
        # Добавляем смещение мыши к рысканью и тангажу:
        self.camera.rotation.y += mouse_delta_xy[0] * (self.mouse_sensitivity * 0.25)  # По горизонтали.
        self.camera.rotation.x -= mouse_delta_xy[1] * (self.mouse_sensitivity * 0.25)  # По вертикали.
        check_mouse_pos(self.input, self.camera, 16, 16)  # Проверяем позицию мыши.

        # Если мы не перемещаемся вверх-вниз в зависимости от направления, ограничиваем взгляд по вертикали на 90 град.:
        if not self.up_is_forward: self.camera.rotation.x = clamp(self.camera.rotation.x, -90, +90)

    # Управление с помощью клавиатуры:
    def keyboard_control(self, delta_time: float) -> None:
        keys = self.input.get_key_pressed()

        # Вращать крен камеры:
        if keys[Key.K_LEFT]:  self.camera.rotation.z -= 25.0 * delta_time
        if keys[Key.K_RIGHT]: self.camera.rotation.z += 25.0 * delta_time
