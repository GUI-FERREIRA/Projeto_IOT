import numpy as np
from control.matlab import *
from threading import Thread
from time import time,sleep

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Levitador:
    def __init__(self):
        s = tf('s')
        m = 0.150
        g = 9.81
        Ca = 0.5
        rho = 1
        r = 0.1
        A = np.pi * r ** 2
        alfa = 0.5 * Ca * rho * A / m
        va_e = np.sqrt(g / alfa)
        k_m = 0.5
        tal = 0.01
        Gb = (2 * alfa * va_e) / (s ** 2)  # Ft do movimento da bolinha
        Gv = k_m / (tal * s + 1)  # Ft da ventoinha
        G = Gv * Gb
        Gs = tf2ss(G)
        self.A = Gs.A
        self.B = Gs.B
        self.h = 1e-4
        self.uk = np.array([0])
        self.xk = np.array([[0], [0], [0]])
        self.data = []

    def x_dot(self, t, x, u):
        A = self.A
        B = self.B
        xkp1 = A @ x + B @ u
        return xkp1

    def rk4(self, tk, xk, uk):
        h = self.h
        xk = xk.reshape([2, 1])
        uk = uk.reshape([1, 1])
        k1 = x_dot(tk, xk, uk)
        k2 = x_dot(tk + h / 2.0, xk + h * k1 / 2.0, uk)
        k3 = x_dot(tk + h / 2.0, xk + h * k2 / 2.0, uk)
        k4 = x_dot(tk + h, xk + h * k3, uk)
        xkp1 = xk + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return xkp1.reshape([2, ])

    def __call__(self):
        t = 0
        while True:
            self.xk = self.rk4(t, self.xk, self.uk)
            self.data.append((t, self.uk[0]))
            t += self.h
            time.sleep(self.h)

    def listenTCP(self):
        pass

    def create_circle(self, x, y, r, canvas, **kw):  # center coordinates, radius
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        return canvas.create_oval(x0, y0, x1, y1, **kw)

    def ui(self):
        details = {'len': 1, 'div': 0.1, 'raio': 24}
        root = tk.Tk()
        root.title('Levitador')
        frame = tk.Frame(root, bg='#0f0')
        frame.grid(row=0, column=0)
        canvas = tk.Canvas(frame, bg='#0a0', width=500, height=500)
        canvas.pack(fill=tk.BOTH, expand=True)
        canvas.create_arc(200, 450, 300, 400 - details['raio'] // 2, fill="#0ab", extent=180)
        canvas.create_rectangle(225, 400, 275, 50, fill='#f00')
        ball = self.create_circle(250, 400 - details['raio'], details['raio'], canvas, fill='#00a')
        details['ylst'] = 400 - details['raio']
        for dy in np.arange(0, details['len'] + details['div'], details['div']):
            y = dy * (325)
            y = 400 - y - details['raio']
            canvas.create_line(275, y, 275 + details['raio'] // 2, y)
            canvas.create_text(277, y - 3, fill="darkblue", font="Times 8", text="%.1f m" % (dy,), anchor=tk.W)

        def setBall():
            t = np.arange(0,2*np.pi,0.01)
            x = np.sin(t)**2
            while True:
                for y in x:
                    y = y * (325)
                    y = 400 - y - details['raio']
                    y = y - details['ylst']
                    details['ylst'] = y + details['ylst']
                    canvas.move(ball, 0, y)
                    sleep(0.001)
        Thread(target=setBall,daemon=True).start()
        root.mainloop()


l = Levitador()
print('runing')
l.ui()
print('end')
