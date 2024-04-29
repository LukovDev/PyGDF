#
# controllers.py - Создаёт классы-контроллеры камеры. Чтобы можно было свободно перемещаться по OpenGL пространству.
#


# Импортируем:
if True:
    import glm


# Проверяем и перемещаем курсор мыши если тот рядом с границей окна:
def check_mouse_pos(window, x_pos_detect: int = 16, y_pos_detect: int = 16) -> None:
    mouse_pos = window.get_mouse_pos()
    set_mouse = window.set_mouse_pos
    win_size = window.get_size()
    if mouse_pos[0] < x_pos_detect:               set_mouse((win_size[0] - x_pos_detect, mouse_pos[1]))
    if mouse_pos[0] > win_size[0] - x_pos_detect: set_mouse((x_pos_detect, mouse_pos[1]))
    if mouse_pos[1] < y_pos_detect:               set_mouse((mouse_pos[0], win_size[1] - y_pos_detect))
    if mouse_pos[1] > win_size[1] - y_pos_detect: set_mouse((mouse_pos[0], y_pos_detect))


# Класс управления 2D камеры:
class CameraController2D:
    def __init__(self, window, keys, camera,
                 offset_scale: float = 1.0,
                 min_zoom:     float = 1/1000,
                 max_zoom:     float = 128000,
                 friction:     float = 0.2) -> None:
        self.window = window
        self.keys   = keys
        self.camera = camera

        self.fixed_mouse_pos = (0, 0)
        self.offset_scale = offset_scale
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.friction = friction
        self.target_pos = glm.vec2(self.camera.position.xy)

    # Обновление камеры:
    def update(self, delta_time: float, gui_pressed_pass: bool = False) -> None:
        mouse_pressed = self.window.get_mouse_pressed()
        mouse_scroll  = self.window.get_mouse_scroll()
        mouse_pos     = self.window.get_mouse_pos()
        mouse_rel     = self.window.get_mouse_rel()
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
            check_mouse_pos(self.window, 16, 16)
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
    def __init__(self, window, keys, camera,
                 mouse_sensitivity: float = 1.0,
                 ctrl_speed:        float = .75,
                 speed:             float = 6,
                 shift_speed:       float = 24,
                 friction:          float = 1,
                 pitch_min:         float = -89,
                 pitch_max:         float = +89,
                 move_up_forward: bool = False) -> None:
        self.window            = window
        self.keys              = keys
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

        self.camera_target = glm.vec3(self.camera.position.xyz)

        self.pressed_pass = False
        self.is_pressed = False

    # Обновление контроллера:
    def update(self, delta_time: float, pressed_pass: bool = False) -> None:
        # Получаем смещение мыши:
        mouse_delta_xy = self.window.get_mouse_rel()

        mdxy = mouse_delta_xy[0]*(self.mouse_sensitivity*0.1), mouse_delta_xy[1]*(self.mouse_sensitivity*0.1)

        # Eсли мы зажали ПКМ и не попали на интерфейс, то могли свободно управлять камерой пока не отпустим ПКМ:        
        if self.window.get_mouse_pressed()[2] and not pressed_pass and not self.is_pressed:
            self.is_pressed = True

        # Если мы попали на интерфейс когда зажали ПКМ, то управлять мы не можем:
        if self.window.get_mouse_pressed()[2] and pressed_pass and not self.is_pressed:
            self.pressed_pass = True

        # Если мы отпустили ПКМ, то всё сбрасываем:
        if not self.window.get_mouse_pressed()[2]:
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

        if round(glm.length(self.camera_target-self.camera.position), 4) > 0.001 or \
           (not (mdxy[0] == 0 and mdxy[1] == 0) and self.window.get_mouse_pressed()[2]):
            self.is_movement = True
        else: self.is_movement = False

        self.camera.update()

    # Управление с помощью мыши:
    def mouse_control(self, mouse_delta_xy: tuple[int, int]) -> None:
        # Добавляем смещение мыши к рысканью и тангажу:
        self.camera.yaw   += mouse_delta_xy[0] * (self.mouse_sensitivity * 0.1)
        self.camera.pitch -= mouse_delta_xy[1] * (self.mouse_sensitivity * 0.1)
        check_mouse_pos(self.window, 16, 16)  # Проверяем позицию мыши.

        # Ограничиваем угол обзора камеры (вверх и вниз):
        self.camera.pitch = glm.clamp(self.camera.pitch, self.pitch_min, self.pitch_max)

    # Управление с помощью клавиатуры:
    def keyboard_control(self, delta_time: float) -> None:
        keys = self.window.get_key_pressed()

        # Если нажимают на левый или правый шифт, ускорить перемещение:
        if keys[self.keys.K_LSHIFT] or keys[self.keys.K_RSHIFT]:
            speed = self.shift_speed * delta_time
        # Иначе если нажимают CTRL:
        elif keys[self.keys.K_LCTRL] or keys[self.keys.K_RCTRL]:
            speed = self.ctrl_speed * delta_time
        else: speed = self.speed * delta_time

        # Настраиваем вектора:
        self.camera.right = glm.normalize(glm.cross(self.camera.forward, glm.vec3(0, 1, 0)))

        if not self.move_up_forward:
            self.camera.forward = -glm.normalize(glm.cross(self.camera.right, glm.vec3(0, 1, 0)))
        else: self.camera.up = glm.cross(-self.camera.forward, self.camera.right)

        # Управление клавишами:
        if keys[self.keys.K_w]: self.camera_target += self.camera.forward * speed
        if keys[self.keys.K_s]: self.camera_target -= self.camera.forward * speed
        if keys[self.keys.K_a]: self.camera_target -= self.camera.right   * speed
        if keys[self.keys.K_d]: self.camera_target += self.camera.right   * speed
        if keys[self.keys.K_q]: self.camera_target -= self.camera.up      * speed
        if keys[self.keys.K_e]: self.camera_target += self.camera.up      * speed
