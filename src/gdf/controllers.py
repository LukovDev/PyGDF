#
# controllers.py - Создаёт классы-контроллеры камеры. Чтобы можно было свободно перемещаться по OpenGL пространству.
#


# Импортируем:
from .input import InputHandler, Key
from .math import *


# Проверяем и перемещаем курсор мыши если тот рядом с границей окна:
def check_mouse_pos(input, camera, x_pos_detect: int = 16, y_pos_detect: int = 16) -> None:
    mouse_pos = input.get_mouse_pos()
    set_mouse = input.set_mouse_pos
    win_size = camera.width, camera.height
    if mouse_pos[0] < x_pos_detect:               set_mouse((win_size[0] - x_pos_detect, mouse_pos[1]))
    if mouse_pos[0] > win_size[0] - x_pos_detect: set_mouse((x_pos_detect, mouse_pos[1]))
    if mouse_pos[1] < y_pos_detect:               set_mouse((mouse_pos[0], win_size[1] - y_pos_detect))
    if mouse_pos[1] > win_size[1] - y_pos_detect: set_mouse((mouse_pos[0], y_pos_detect))


# Класс управления 2D камеры:
class CameraController2D:
    def __init__(self, input: InputHandler, camera,
                 offset_scale: float = 1.0,
                 min_zoom:     float = 1/1000,
                 max_zoom:     float = 128000,
                 friction:     float = 0.2) -> None:
        self.input = input
        self.camera = camera

        self.fixed_mouse_pos = (0, 0)
        self.offset_scale = offset_scale
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.friction = friction
        self.target_pos = vec2(self.camera.position.xy)

    # Обновление камеры:
    def update(self, delta_time: float, gui_pressed_pass: bool = False) -> None:
        mouse_pressed = self.input.get_mouse_pressed()
        mouse_scroll  = self.input.get_mouse_scroll()
        mouse_pos     = self.input.get_mouse_pos()
        mouse_rel     = self.input.get_mouse_rel()
        is_zooming    = not gui_pressed_pass or mouse_pressed[0]

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

        self.camera.update()


# Класс управления 3D камеры:
class CameraController3D:
    def __init__(self, input: InputHandler, camera,
                 mouse_sensitivity: float = 1.0,
                 ctrl_speed:        float = .75,
                 speed:             float = 6,
                 shift_speed:       float = 24,
                 friction:          float = 1,
                 pitch_min:         float = -89,
                 pitch_max:         float = +89,
                 move_up_forward: bool = False) -> None:
        self.input             = input
        self.camera            = camera

        self.mouse_sensitivity = mouse_sensitivity
        self.ctrl_speed        = ctrl_speed
        self.speed             = speed
        self.shift_speed       = shift_speed

        self.is_movement       = False

        self.friction          = friction
        self.pitch_min         = pitch_min
        self.pitch_max         = pitch_max
        self.move_up_forward   = move_up_forward

        self.camera_target = vec3(self.camera.position.xyz)

        self.pressed_pass = False
        self.is_pressed = False

    # Обновление контроллера:
    def update(self, delta_time: float, pressed_pass: bool = False) -> None:
        # Получаем смещение мыши:
        mouse_delta_xy = self.input.get_mouse_rel()

        mdxy = mouse_delta_xy[0]*(self.mouse_sensitivity*0.1), mouse_delta_xy[1]*(self.mouse_sensitivity*0.1)

        # Eсли мы зажали ПКМ и не попали на интерфейс, то могли свободно управлять камерой пока не отпустим ПКМ:        
        if self.input.get_mouse_pressed()[2] and not pressed_pass and not self.is_pressed:
            self.is_pressed = True

        # Если мы попали на интерфейс когда зажали ПКМ, то управлять мы не можем:
        if self.input.get_mouse_pressed()[2] and pressed_pass and not self.is_pressed:
            self.pressed_pass = True

        # Если мы отпустили ПКМ, то всё сбрасываем:
        if not self.input.get_mouse_pressed()[2]:
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

        if round(length(self.camera_target-self.camera.position), 4) > 0.001 or \
           (not (mdxy[0] == 0 and mdxy[1] == 0) and self.input.get_mouse_pressed()[2]):
            self.is_movement = True
        else: self.is_movement = False

        self.camera.update()

    # Управление с помощью мыши:
    def mouse_control(self, mouse_delta_xy: tuple[int, int]) -> None:
        # Добавляем смещение мыши к рысканью и тангажу:
        self.camera.yaw   += mouse_delta_xy[0] * (self.mouse_sensitivity * 0.1)
        self.camera.pitch -= mouse_delta_xy[1] * (self.mouse_sensitivity * 0.1)
        check_mouse_pos(self.input, self.camera, 16, 16)  # Проверяем позицию мыши.

        # Ограничиваем угол обзора камеры (вверх и вниз):
        self.camera.pitch = clamp(self.camera.pitch, self.pitch_min, self.pitch_max)

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

        # Настраиваем вектора:
        self.camera.right = normalize(cross(self.camera.forward, vec3(0, 1, 0)))

        if not self.move_up_forward:
            self.camera.forward = -normalize(cross(self.camera.right, vec3(0, 1, 0)))
        else: self.camera.up = cross(-self.camera.forward, self.camera.right)

        # Управление клавишами:
        if keys[Key.K_w]: self.camera_target += self.camera.forward * speed
        if keys[Key.K_s]: self.camera_target -= self.camera.forward * speed
        if keys[Key.K_a]: self.camera_target -= self.camera.right   * speed
        if keys[Key.K_d]: self.camera_target += self.camera.right   * speed
        if keys[Key.K_q]: self.camera_target -= self.camera.up      * speed
        if keys[Key.K_e]: self.camera_target += self.camera.up      * speed
