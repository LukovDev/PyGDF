#
# skybox.py - Создаёт класс для отрисовки неба используя 6 текстур.
#


# Импортируем:
if True:
    from .gl import *
    from .texture import Texture
    from .camera import Camera3D


# Класс неба:
class SkyBox:
    # Класс кубического неба:
    class CubeMap:
        def __init__(self,
                     up:     Texture,
                     down:   Texture,
                     front:  Texture,
                     back:   Texture,
                     left:   Texture,
                     right:  Texture,
                     camera: Camera3D) -> None:
            self.camera = camera
            self.textures = [
                up, down,
                front, back,
                left, right
            ]

            s = 1  # Половина размера куба неба.

            # Вершины скайбокса:
            self.vertices = [
                [-s, -s, -s, 0, 1], [+s, -s, -s, 1, 1], [+s, +s, -s, 1, 0], [-s, +s, -s, 0, 0],
                [-s, +s, +s, 1, 0], [+s, +s, +s, 0, 0], [+s, -s, +s, 0, 1], [-s, -s, +s, 1, 1],
                [-s, +s, -s, 0, 1], [+s, +s, -s, 1, 1], [+s, +s, +s, 1, 0], [-s, +s, +s, 0, 0],
                [+s, -s, -s, 1, 0], [-s, -s, -s, 0, 0], [-s, -s, +s, 0, 1], [+s, -s, +s, 1, 1],
                [-s, +s, -s, 1, 0], [-s, +s, +s, 0, 0], [-s, -s, +s, 0, 1], [-s, -s, -s, 1, 1],
                [+s, +s, +s, 1, 0], [+s, +s, -s, 0, 0], [+s, -s, -s, 0, 1], [+s, -s, +s, 1, 1]
            ]

        # Отрисовать скайбокс:
        def render(self) -> None:
            def draw_face(vertices: list, texture) -> None:
                gl.glBindTexture(gl.GL_TEXTURE_2D, texture.id)
                gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
                gl.glBegin(gl.GL_QUADS)
                for vert in vertices: gl.glTexCoord2f(vert[3], vert[4]) ; gl.glVertex3d(vert[0], vert[1], vert[2])
                gl.glEnd()

            gl.glMatrixMode(gl.GL_MODELVIEW)
            gl.glPushMatrix()
            is_enabled_cull_face = True if gl.glIsEnabled(gl.GL_CULL_FACE) else False
            is_enabled_lighting = True if gl.glIsEnabled(gl.GL_LIGHTING) else False
            gl.glScale(1, 1, 1)
            gl.glTranslated(*self.camera.position.xyz)
            gl.glDisable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_CULL_FACE)
            gl.glEnable(gl.GL_TEXTURE_2D)
            gl.glColor(1, 1, 1)

            draw_face(self.vertices[8:12],  self.textures[0])  # UP.
            draw_face(self.vertices[12:16], self.textures[1])  # DOWN.
            draw_face(self.vertices[:4],    self.textures[2])  # FRONT.
            draw_face(self.vertices[4:8],   self.textures[3])  # BACK.
            draw_face(self.vertices[16:20], self.textures[4])  # LEFT.
            draw_face(self.vertices[20:],   self.textures[5])  # RIGHT.

            gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
            if not is_enabled_cull_face: gl.glDisable(gl.GL_CULL_FACE)
            if is_enabled_lighting: gl.glEnable(gl.GL_LIGHTING)
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glPopMatrix()
