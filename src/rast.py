import numpy as np
from math import floor
from numba import njit

@njit(cache=True)
def get_barr(x, y, x0, y0, x1, y1, x2, y2):
    denom = (x0 - x2) * (y1 - y2) - (x1 - x2) * (y0 - y2)
    if denom == 0.0:
        return -1.0, -1.0, -1.0

    lambda0 = ((x - x2) * (y1 - y2) - (x1 - x2) * (y - y2)) / denom
    lambda1 = ((x0 - x2) * (y - y2) - (x - x2) * (y0 - y2)) / denom
    lambda2 = 1.0 - lambda0 - lambda1
    return lambda0, lambda1, lambda2


@njit(cache=True)
def print_treug(px0, py0, z0, px1, py1, z1, px2, py2, z2, img_mat, color, z_buffer):
    xmin = floor(max(min(min(px0, px1), px2), 0.0))
    ymin = floor(max(min(min(py0, py1), py2), 0.0))
    xmax = floor(min(max(max(px0, px1), px2), img_mat.shape[1] - 1))
    ymax = floor(min(max(max(py0, py1), py2), img_mat.shape[0] - 1))

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

@njit(cache=True)
def get_normal(x0, y0, z0, x1, y1, z1, x2, y2, z2):
    ux = x1 - x2
    uy = y1 - y2
    uz = z1 - z2
    vx = x1 - x0
    vy = y1 - y0
    vz = z1 - z0

    nx = uy * vz - uz * vy
    ny = uz * vx - ux * vz
    nz = ux * vy - uy * vx
    return nx, ny, nz

@njit(cache=True)
def get_normal_cross(nx, ny, nz, lx, ly, lz):
    dot_nl = nx * lx + ny * ly + nz * lz
    norm_n = np.sqrt(nx * nx + ny * ny + nz * nz)
    norm_l = np.sqrt(lx * lx + ly * ly + lz * lz)

    if norm_n == 0.0 or norm_l == 0.0:
        return 0.0
    return dot_nl / (norm_n * norm_l)

