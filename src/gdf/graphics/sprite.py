#
# sprite.py - Создаёт класс спрайта. Просто позволяет отрисовывать текстуру.
#


# Импортируем:
from .gl import *
from .atlas import AtlasTexture
from .texture import Texture
from .texunits import TextureUnits
from .render import RenderPipeline
from ..math import *


# Класс 2D спрайта:
class Sprite2D:
    def __init__(self, texture: Texture|AtlasTexture = None) -> None:
        self.texture = texture
        self.id      = 0
        self.width   = 1
        self.height  = 1

        # Если текстурка указана:
        if self.texture is not None:
            self.id     = self.texture.id
            self.width  = self.texture.width
            self.height = self.texture.height

    # Отрисовка:
    def render(self,
               x:      float,
               y:      float,
               width:  float = None,
               height: float = None,
               angle:  float = 0.0,
               color:  vec3|vec4 = None,
               custom_shader: bool = False) -> "Sprite2D":
        if color is None: color = vec4(1.0)
        if isinstance(color, (vec3, glm.vec3)): color = vec4(color, 1.0)

        # Рисуем спрайт:
        def _render_sprite_() -> None:
            RenderPipeline.Sprite.vao.begin()
            RenderPipeline.Sprite.vvbo.render_elements(count=6)
            RenderPipeline.Sprite.vao.end()

        # Если текстурка указана:
        if self.texture is not None:
            self.id     = self.texture.id
            self.width  = self.texture.width
            self.height = self.texture.height

        # Матрица преобразования спрайта:
        wdth, hght = width if width is not None else self.width, height if height is not None else self.height
        matrix = glm.scale(glm.translate(mat4(1.0), vec3(x+wdth/2.0, y+hght/2.0, 0.0)), vec3(wdth/2.0, hght/2.0, 0.0))
        if angle != 0.0: matrix = glm.rotate(matrix, radians(angle), vec3(0, 0, 1))

        # Обновляем данные в шейдере:
        if not custom_shader:
            RenderPipeline.default_shader.begin()
            # Если текстуры нет, рисуем без неё. Если она есть, перепривязываем и рисуем с ней:
            if self.texture is not None:
                RenderPipeline.default_shader.set_uniform("u_use_texture", True)
                RenderPipeline.default_shader.set_sampler("u_texture", TextureUnits.rebind(self.texture, 0))
            else: RenderPipeline.default_shader.set_uniform("u_use_texture", False)
            RenderPipeline.default_shader.set_uniform("u_color", color)
            RenderPipeline.default_shader.set_uniform("u_model", matrix)
            _render_sprite_()
            RenderPipeline.default_shader.end()
        else: _render_sprite_()

        return self

    # Удалить спрайт:
    def destroy(self) -> None:
        self.texture.destroy()


# Класс 3D спрайта:
class Sprite3D:
    def __init__(self, texture: Texture|AtlasTexture = None) -> None:
        self.texture = texture
        self.id      = 0
        self.width   = 1
        self.height  = 1

        # Если текстурка указана:
        if self.texture is not None:
            self.id     = self.texture.id
            self.width  = self.texture.width
            self.height = self.texture.height

    # Отрисовка:
    def render(self,
               position: vec3,
               size:     vec2,
               rotation: vec3,
               color:    vec3|vec4 = None,
               custom_shader: bool = False) -> "Sprite2D":
        if color is None: color = vec4(1.0)
        if isinstance(color, (vec3, glm.vec3)): color = vec4(color, 1.0)

        # Рисуем спрайт:
        def _render_sprite_() -> None:
            RenderPipeline.Sprite.vao.begin()
            RenderPipeline.Sprite.vvbo.render_elements(count=6)
            RenderPipeline.Sprite.vao.end()

        # Если текстурка указана:
        if self.texture is not None:
            self.id     = self.texture.id
            self.width  = self.texture.width
            self.height = self.texture.height

        # Матрица преобразования спрайта:
        if size is not None: wdth, hght = size.xy
        else: wdth, hght = self.width, self.height
        matrix = glm.translate(mat4(1.0), position.xyz)
        matrix = glm.rotate(matrix, radians(rotation.z), vec3(0, 0, 1))
        matrix = glm.rotate(matrix, radians(rotation.x), vec3(1, 0, 0))
        matrix = glm.rotate(matrix, radians(rotation.y), vec3(0, 1, 0))
        matrix = glm.scale(matrix, vec3(wdth/2, hght/2, 0.0))

        # Обновляем данные в шейдере:
        if not custom_shader:
            RenderPipeline.default_shader.begin()
            # Если текстуры нет, рисуем без неё. Если она есть, перепривязываем и рисуем с ней:
            if self.texture is not None:
                RenderPipeline.default_shader.set_uniform("u_use_texture", True)
                RenderPipeline.default_shader.set_sampler("u_texture", TextureUnits.rebind(self.texture, 0))
            else: RenderPipeline.default_shader.set_uniform("u_use_texture", False)
            RenderPipeline.default_shader.set_uniform("u_color", color)
            RenderPipeline.default_shader.set_uniform("u_model", matrix)
            _render_sprite_()
            RenderPipeline.default_shader.end()
        else: _render_sprite_()

        return self

    # Удалить спрайт:
    def destroy(self) -> None:
        self.texture.destroy()
