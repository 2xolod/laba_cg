import numpy as np
from PIL import Image, ImageTk
from cfg import height, width, zoom, IMAGES, offset_y, offset_x, light
from src.scene import Scene
from src.renderer import Renderer
import tkinter as tk


img_mat = np.zeros((height, width, 3), dtype=np.uint8)
def reset_img_mat():
    global img_mat
    img_mat = np.zeros((height, width, 3), dtype=np.uint8)


# img_mat = reset_img_mat()
z_buffer = np.full((height, width), np.inf)
scene = Scene("model.obj")
renderer = Renderer(width, height, zoom, offset_x, offset_y, light)

renderer.render(img_mat, z_buffer, scene)
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
            self.renderer.zoom *= 1.1
        elif k == 'minus':
            self.renderer.zoom /= 1.1
        else:
            return

        self.render()
        # Не обрабатываем дальше – return 'brake'
        return 'break'

    def render(self):
        # reset_img_mat()
        self.renderer.render(img_mat, z_buffer, self.scene)
        self.full_image = Image.fromarray(img_mat)
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
        s = min(ww / width, wh / height)
        dw = max(1, int(width * s))
        dh = max(1, int(height * s))
        disp = self.full_image.resize((dw, dh), Image.BILINEAR)
        # Очень важно сохранить ImageTk.PhotoImage(disp) в поле класса
        # Если оно будет локальным, то удалится после выхода сборщиком мусора
        self.photo = ImageTk.PhotoImage(disp)
        self.canvas.delete('all')
        self.canvas.create_image(ww // 2, wh // 2, image=self.photo)

    # скопировать как есть
    def run(self):
        self.root.mainloop()


img = Image.fromarray(img_mat)
img.save(IMAGES + "/img1.png")
if __name__ == '__main__':
    App(scene, renderer, width, height).run()