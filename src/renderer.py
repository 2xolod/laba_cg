import numpy as np
from src.rast import get_normal, get_normal_cross, print_treug


class Renderer:

    def __init__(self, width, height, zoom, offset_x, offset_y, light):
        self.width = width
        self.height = height
        self.zoom = zoom
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.light = light

    def render(self, img_mat, z_buffer, scene):
        render(img_mat, z_buffer, scene,
               self.width, self.height, self.zoom,
               self.offset_x, self.offset_y, self.light
               )



def render(img_mat, z_buffer, scene, width, height, zoom, offset_x, offset_y, light):
    for i in scene.fs:
        v0 = scene.coords[i[0]]
        v1 = scene.coords[i[1]]
        v2 = scene.coords[i[2]]

        x0, y0, z0 = v0[0], v0[1], v0[2]
        x1, y1, z1 = v1[0], v1[1], v1[2]
        x2, y2, z2 = v2[0], v2[1], v2[2]

        normal = get_normal(x0, y0, z0, x1, y1, z1, x2, y2, z2)
        normal_cross = get_normal_cross(normal, light)

        if normal_cross < 0:
            px0 = x0 * zoom + offset_x
            py0 = -y0 * zoom + offset_y
            px1 = x1 * zoom + offset_x
            py1 = -y1 * zoom + offset_y
            px2 = x2 * zoom + offset_x
            py2 = -y2 * zoom + offset_y

            color = np.array([-255 * normal_cross, 0, 0])

            print_treug(px0, py0, z0,
                        px1, py1, z1,
                        px2, py2, z2,
                        img_mat, color, z_buffer
                        )