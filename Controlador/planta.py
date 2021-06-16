import numpy as np
from control.matlab import *
from threading import Thread
from time import time, sleep
import socket
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Atomic import *

class Levitador:
    def __init__(self, tempoAmostragemCompensador=0.01,host='localhost',port=8909):
        self.Ts = tempoAmostragemCompensador
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

        self.tensao = 0
        
        self.canvas = None
        self.y = Atomic(0)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.details = {}
    
    def x_dot(self, t, x, u):
        A = self.A
        B = self.B
        xkp1 = A @ x + B @ u
        return xkp1

    def rk4(self, tk, xk, uk):
        h = self.h
        xk = xk.reshape([3, 1])
        uk = uk.reshape([1, 1])
        k1 = self.x_dot(tk, xk, uk)
        k2 = self.x_dot(tk + h / 2.0, xk + h * k1 / 2.0, uk)
        k3 = self.x_dot(tk + h / 2.0, xk + h * k2 / 2.0, uk)
        k4 = self.x_dot(tk + h, xk + h * k3, uk)
        xkp1 = xk + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        return xkp1.reshape([3, 1])

    def __call__(self):
        t = 0
        while True:
            self.uk[0]= self.tensao
            self.xk = self.rk4(t, self.xk, self.uk)
            y = self.xk[0,0]
            if y<0:
                self.xk[0] = 0
                self.xk[1] = self.xk[1]*-0.95
            if y>1:
                self.xk[0] = 1
                self.xk[1] = 0
            
            self.setBall(y)
            t += self.h
            self.y.value = y
            sleep(self.h)


    def amostrador(self):
        while True:
            sleep(self.Ts)
            v = self.y.value
            self.socket.send(np.array(v, dtype=np.float64).tobytes())
            

    def listenTCP(self):
        while True:
            bytes = self.socket.recv(8)
            v = np.frombuffer(bytes, dtype=np.float64)
            self.tensao = v[0]
    

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
        self.canvas = canvas
        details['ball'] = ball
       
        self.details = details 
        root.mainloop()

    def setBall(self, y):
        if self.canvas is None:  # verifica se a ui ja foi iniciada
            return
        y = y * (325)
        y = 400 - y - self.details['raio']
        y = y - self.details['ylst']
        self.details['ylst'] = y + self.details['ylst']
        self.canvas.move(self.details['ball'], 0, y)
        


if __name__ == '__main__':
    l = Levitador(0.01)
    Thread(target=l.amostrador).start()
    Thread(target=l.listenTCP).start()
    Thread(target=l).start()
    l.ui()
