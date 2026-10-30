import numpy as np
from math import floor
from cfg import light, OBJECTS


class Model:
    
    def __init__(self, img_mat, zoom, z_buffer):
        self.full_coords = []
        self.img_mat = img_mat
        self.coords = []
        self.zoom = zoom
        self.fs = []
        self.z_buffer = z_buffer
        self.open_coords()  
        # print(self.coords)
    
    
    def open_coords(self):
        with open(OBJECTS + "/model.obj") as file:
            for line in file:
                sp = line.split()
                # add_el = 
                if sp[0] == "v":
                    add_el = np.array(list(map(float, sp[1:])))
                    self.coords.append(add_el)
                elif sp[0] == "f":
                    add_el = np.array(list([int(x.split("/")[0]) - 1 for x in sp[1:]]))
                    self.fs.append(add_el)
                else:
                    add_el = sp
                self.full_coords.append(add_el)

            # print(self.fs)

    def print_line(self, x0, y0, x1, y1):
        dmax = max(abs(abs(floor(x0)) - abs(floor(x1))), abs(abs(floor(y0)) - abs(floor(y1))))

        L = dmax + 1
        if L == 1:
            self.img_mat[-floor(y0), floor(x0)] = 255
            return
        
        dx = (x1 - x0)/(L - 1)
        dy = (y1 - y0)/(L - 1)

        x = x0
        y = y0

        # while (floor(x) != floor(x1) and floor(y) != floor(y1)):
        for _ in range(L):
            self.img_mat[-floor(y), floor(x)] = 255
            x += dx
            y += dy

    def print_coords(self):
        for coord in self.coords:
            self.img_mat[-floor(coord[1] * self.zoom + self.zoom // 10), floor(coord[0] * self.zoom + self.zoom // 10)] = 255

    def print_poligons(self):
        for i in self.fs:
            normal = self.get_normal(
                self.coords[i[0]][0] * self.zoom + self.zoom // 10, -self.coords[i[0]][1] * self.zoom + self.zoom // 10, self.coords[i[0]][2] * self.zoom + self.zoom // 10,
                self.coords[i[1]][0] * self.zoom + self.zoom // 10, -self.coords[i[1]][1] * self.zoom + self.zoom // 10, self.coords[i[1]][2] * self.zoom + self.zoom // 10,
                self.coords[i[2]][0] * self.zoom + self.zoom // 10, -self.coords[i[2]][1]* self.zoom + self.zoom // 10, self.coords[i[2]][2] * self.zoom + self.zoom // 10)
            normal_cross = -self.get_normal_cross(normal, light)
            color = np.array([-255 * normal_cross, 0, 0])
            if normal_cross < 0:
                self.print_treug(
                                self.coords[i[0]][0] * self.zoom + self.zoom // 10, -self.coords[i[0]][1] * self.zoom + self.zoom // 10, self.coords[i[0]][2] * self.zoom + self.zoom // 10,
                                self.coords[i[1]][0] * self.zoom + self.zoom // 10, -self.coords[i[1]][1] * self.zoom + self.zoom // 10, self.coords[i[1]][2] * self.zoom + self.zoom // 10,
                                self.coords[i[2]][0] * self.zoom + self.zoom // 10, -self.coords[i[2]][1]* self.zoom + self.zoom // 10, self.coords[i[2]][2] * self.zoom + self.zoom // 10,
                                self.img_mat, color, self.z_buffer
                                )

    def print_model(self):
        self.print_poligons()
    
    @staticmethod
    def get_barr(x, y, x0, y0, x1, y1, x2, y2):
        lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
        lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
        lambda2 = 1 - lambda0 - lambda1
        return lambda0, lambda1, lambda2

    @staticmethod
    def print_treug(x0, y0, z0, x1, y1, z1, x2, y2, z2, img_mat, color, z_buffer):
        xmin = floor(max(min(x0, x1, x2), 0))
        ymin = floor(max(min(y0, y1, y2), 0))
        xmax = floor(max(x0, x1, x2))
        ymax = floor(max(y0, y1, y2))
        # rect = [xmin,]
        for x in range(xmin, xmax + 1):
            for y in range(ymin, ymax + 1):
                barr_xy = Model.get_barr(x, y, x0, y0, x1, y1, x2, y2)
                if all(map(lambda x: x > 0, barr_xy)):
                    z_pol = barr_xy[0] * z0 + barr_xy[1] * z1 + barr_xy[2] * z2
                    if z_pol > z_buffer[x, y]:
                        continue
                    else:    
                        img_mat[y, x][0] = color[0]
                        img_mat[y, x][1] = color[1]
                        img_mat[y, x][2] = color[2]
                        z_buffer[x, y] = z_pol
                # elif all(map(lambda x: x > 0, barr_xy))
                else:
                    continue
    @staticmethod
    def get_normal(x0, y0, z0, x1, y1, z1, x2, y2, z2):
        return np.cross(np.array([x1 - x2, y1 - y2, z1 - z2]), np.array([x1 - x0, y1 - y0, z1 - z0]))

    @staticmethod
    def get_normal_cross(n, l):
        return np.dot(n, l)/(np.linalg.norm(n) * np.linalg.norm(l))



                
