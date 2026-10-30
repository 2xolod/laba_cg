import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
import random

class Scene:
    def __init__(self, seed = 42):
        random.seed(seed)
        self.spheres = []
        for _ in range(100):
            sx = random.uniform(-1.0, 1.0)
            sy = random.uniform(-1.0, 1.0)
            sz = random.uniform(-1.0, 1.0)
            sr = random.uniform(0.025, 0.1)
            cr = random.randint(60, 255) / 255.0
            cg = random.randint(60, 255) / 255.0
            cb = random.randint(60, 255) / 255.0
            self.spheres.append((sx, sy, sz, sr, np.array([cr, cg, cb])))

        self.lights = [
            np.array([ 2.0,  2.0,  -2.0]),
            np.array([-2.0,  1.0,  -2.0]),
            np.array([ 0.0, -1.5,  -2.5]),
        ]

        self.ambient   = 0.08
        self.diffuse   = 0.25
        self.specular  = 0.2
        self.shininess = 4

class Renderer:
    def __init__(self, W, H, scale):
        self.H, self.W = H, W
        self.scale = scale

        self.img  = np.zeros((H, W, 3), dtype=np.uint8)
        self.zbuf = np.full((H, W), np.inf, dtype=np.float32)

        self.cx = self.W / 2.0
        self.cy = self.H / 2.0

    def shade_pixel(self, dx, dy, sx, sy, sz, sr, base_color,
                    lights, ambient, diffuse, specular, shininess):
        r2 = dx*dx + dy*dy
        if r2 > sr*sr:
            return None
        dz = np.sqrt(sr*sr - r2)

        normal = np.array([dx/sr, dy/sr, -dz/sr])
        point  = np.array([sx + dx, sy + dy, sz - dz])
        view   = np.array([0.0, 0.0, -1.0])

        color = ambient * base_color

        for light_pos in lights:
            to_light = light_pos - point
            dist     = np.linalg.norm(to_light)
            L        = to_light / dist

            ndl = np.dot(normal, L)
            if ndl <= 0.0:
                continue

            R    = 2.0 * ndl * normal - L
            ndv  = np.dot(R, view)
            spec = (ndv ** shininess) if ndv > 0.0 else 0.0

            color = color + diffuse * base_color * ndl + specular * spec

        return color, sz - dz

    def render(self, scene):
        self.img  = np.zeros((self.H, self.W, 3), dtype=np.uint8)
        self.zbuf = np.full((self.H, self.W), np.inf, dtype=np.float32)
        for (sx, sy, sz, sr, base_color) in scene.spheres:
            cx_px = sx * self.scale + self.cx
            cy_px = -sy * self.scale + self.cy
            sr_px = sr * self.scale

            x0 = int(cx_px - sr_px); x1 = int(cx_px + sr_px)
            y0 = int(cy_px - sr_px); y1 = int(cy_px + sr_px)
            if x0 < 0:    x0 = 0
            if y0 < 0:    y0 = 0
            if x1 >= self.W:   x1 = self.W - 1
            if y1 >= self.H:   y1 = self.H - 1
            if x0 > x1 or y0 > y1:
                continue

            for py in range(y0, y1 + 1):
                for px in range(x0, x1 + 1):
                    dx, dy = (px - cx_px) / self.scale, -(py - cy_px) / self.scale
                    result = self.shade_pixel(dx, dy, sx, sy, sz, sr, base_color,
                                scene.lights, scene.ambient,
                                scene.diffuse, scene.specular,
                                scene.shininess)
                    if result is None:
                        continue
                    color, z = result
                    if z < self.zbuf[py, px]:
                        self.zbuf[py, px] = z
                        self.img[py, px] = [
                            min(255, int(255 * color[0])),
                            min(255, int(255 * color[1])),
                            min(255, int(255 * color[2])),
                        ]

class App:
    def __init__(self, scene, renderer, win_w = 900, win_h = 900):
        self.scene = scene
        self.renderer = renderer

        # Оставляем как есть
        # Окно верхнего уровня
        self.root = tk.Tk()
        # Размеры окна
        self.root.geometry(f"{win_w}x{win_h}")
        # Область для рисования внутри окна
        self.canvas = tk.Canvas(self.root, bg='black', highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.focus_set()
        # Обновление изображения при изменении размеров окна
        self.canvas.bind('<Configure>', lambda e: self._refit())
        # Привязка обработчика клавиш
        self.root.bind('<Key>', self.on_key)

        # Изображение внутри окна
        self.photo = None
        self.full_image = None

        self.render()

    def on_key(self, event):
        k = event.keysym

        if k == 'plus':
            self.renderer.scale *= 1.1
        elif k == 'minus':
            self.renderer.scale /= 1.1
        else:
            return

        self.render()
        # Не обрабатываем дальше – return 'brake'
        return 'break'

    def render(self):
        self.renderer.render(self.scene)
        self.full_image = Image.fromarray(self.renderer.img)
        self._refit()

    # скопировать как есть
    def _refit(self):
        # Если ещё не отрендерилось, пропускаем
        if self.full_image is None: return
        # Ширина и высота области для рисования
        ww = self.canvas.winfo_width()
        wh = self.canvas.winfo_height()
        # Если вдруг сделали область слишком маленькой
        if ww < 10 or wh < 10: return
        # Вписать с сохранением пропорций
        s = min(ww / self.renderer.W, wh / self.renderer.H)
        dw = max(1, int(self.renderer.W * s))
        dh = max(1, int(self.renderer.H * s))
        disp = self.full_image.resize((dw, dh), Image.BILINEAR)
        # Очень важно сохранить ImageTk.PhotoImage(disp) в поле класса
        # Если оно будет локальным, то удалится после выхода сборщиком мусора
        self.photo = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(ww // 2, wh // 2, image=self.photo)

    # скопировать как есть
    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    scene = Scene()
    renderer = Renderer(1000, 1000, 1000.0)
    App(scene, renderer, 500, 500).run()