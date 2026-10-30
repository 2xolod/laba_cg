import numpy as np
from math import floor


def get_barr(x, y, x0, y0, x1, y1, x2, y2):
    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / ((x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2))
    lambda2 = 1 - lambda0 - lambda1
    return lambda0, lambda1, lambda2



def print_treug(px0, py0, z0, px1, py1, z1, px2, py2, z2, img_mat, color, z_buffer):
    xmin = floor(max(min(px0, px1, px2), 0))
    ymin = floor(max(min(py0, py1, py2), 0))
    xmax = floor(min(max(px0, px1, px2), img_mat.shape[1] - 1))
    ymax = floor(min(max(py0, py1, py2), img_mat.shape[0] - 1))
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            l0, l1, l2 = get_barr(x, y, px0, py0, px1, py1, px2, py2)
            if l0 >= 0 and l1 >= 0 and l2 >= 0:
                    z_pol = l0 * z0 + l1 * z1 + l2 * z2
                    if z_pol < z_buffer[y, x]:
                        z_buffer[y, x] = z_pol
                        img_mat[y, x][0] = color[0]
                        img_mat[y, x][1] = color[1]
                        img_mat[y, x][2] = color[2]


def get_normal(x0, y0, z0, x1, y1, z1, x2, y2, z2):
    return np.cross(np.array([x1 - x2, y1 - y2, z1 - z2]), np.array([x1 - x0, y1 - y0, z1 - z0]))


def get_normal_cross(n, l):
    return np.dot(n, l)/(np.linalg.norm(n) * np.linalg.norm(l))

