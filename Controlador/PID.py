import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import sleep
import socket
from threading import Thread

class PID:
    def __init__(self, host='', porta=8909):
        self.Ts = 0.01
        self.kp = 50
        self.ki = 400
        self.kd = 25000
        self.setPoint = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, porta))
        self.data = []
        # tensao minima e maxima de saída
        self.mn, self.mx = 0.0, 300.0
        # variaveis para eq de difernecas
        #self.e, self.u= [0]*3,[0]*3
        self.ek_1 = 0
        
    def eqdif(self, y):
        '''
        Recebe a posicao atual da bolinha
        :return: a tensão de entrada para o levitador
        '''  
        ek_1 = self.ek_1
        ek = self.setPoint - y
        u = self.kp * ek + self.ki * (ek + ek_1) + self.kd * (ek - ek_1)
        if u > self.mx:
            u = self.mx
        elif u < self.mn:
            u = self.mn
        self.ek_1 = ek 
        return u

    def listenTcp(self):
        self.socket.listen()
        con, client = self.socket.accept()
        print(client, 'has been conneted!')
        while True:
            bytes = con.recv(8)
            y = np.frombuffer(bytes, dtype=np.float64)
            y_ = y[0]
            #print('recebi',y)
            tensao = self.eqdif(y_)
            con.send(np.array(tensao, dtype=np.float64).tobytes())
            #print(type(y),type(tensao))
            self.data.append((y_, tensao))
            #print('pid',y,tensao,self.setPoint)
            

    def ui(self):
        root = tk.Tk()
        dimensao = (720, 540)
        root.geometry("%dx%d" % dimensao)
        obj = {'scdim': dimensao}
        frame_posicaoBola = tk.Frame(root, bg='#0f0')
        frame_saidaCompensador = tk.Frame(root, bg='#00f')
        frameBotoes = tk.Frame(root)

        root.title('Controle de Posição')
        self.uiBotoes(frameBotoes, obj)
        frame_posicaoBola.place(x=1, y=35, width=obj['scdim'][0], height=obj['scdim'][1] / 2 - 20)
        frame_saidaCompensador.place(x=1, y=obj['scdim'][1] / 2 + 20, width=obj['scdim'][0],
                                     height=obj['scdim'][1] / 2 - 20)
        frameBotoes.place(x=1, y=1, width=obj['scdim'][0], height=40)
        pltY = self.putGraphics(frame_posicaoBola, obj['scdim'][0], obj['scdim'][1] / 2 - 20, 'Posição da Bola', 2,legend=['Posição da Bola', 'Posição alvo'],ylim=[-0.5,1.5])
        pltVa = self.putGraphics(frame_saidaCompensador, obj['scdim'][0], obj['scdim'][1] / 2 - 20, 'Tensão do motor',ylim=[-1+self.mn,self.mx+1])
        obj['len'] = 10000

        def loop():
            t, y, v, goal = [0], [0], [0], [self.setPoint]
            while True:
                if len(self.data) < 70:
                   sleep(0.7)
                   continue
                data = self.data[:]
                del self.data[1:len(data)]
                data.pop(0)
                y_ = [dt[0] for dt in data]
                tensao_ = [dt[1] for dt in data]
                y = y + y_
                v = v + tensao_
                t = t + list(t[-1] + self.Ts + np.arange(0, np.size(y_)) * self.Ts)
                goal = goal + list(np.array(y_) * 0 + self.setPoint)
                if len(y) > obj['len']:
                    y = y[len(y) - obj['len']:]
                    v = v[len(v) - obj['len']:]
                    t = t[len(t) - obj['len']:]
                    goal = goal[len(goal) - obj['len']:]
                
                pltY(t, y, t, goal)
                pltVa(t,v)
                
        Thread(target=loop, daemon=True).start()
        root.mainloop()

    def putGraphics(self, frame, x=100, y=100, title='', data=1, legend=['Tensão(V)'],ylim = [-15,15]):
        figure = plt.Figure(figsize=(6, 6), dpi=100)
        ax = figure.add_subplot(111)
        cv = FigureCanvasTkAgg(figure, frame)
        cv.get_tk_widget().place(x=0, y=0, width=x, height=y)
        if data == 1:
            gp, = ax.step([0], [0])
        else:
            gp, gp2 = ax.step([0], [0], [0], [0])
        ax.set_title(title)
        ax.set_ylim(*ylim)
        ax.grid()
        ax.legend(legend)
        if data == 1:
            def plot(x, y):
                gp.set_data(x, y)
                ax.set_xlim(x[0], x[-1])
                frame.after(1,cv.draw)
        else:
            def plot(x, y, w, z):
                gp.set_data(x, y)
                gp2.set_data(w, z)
                ax.set_xlim(x[0], x[-1])
                frame.after(1,cv.draw)
        return plot

    def uiBotoes(self, frame, obj):
        tk.Label(frame, text='Posição').place(x=1, y=10, width=100)
        value = tk.DoubleVar(frame)
        valueStr = tk.StringVar(frame)
        valueStr.set('0')
        value.set(0)

        def chose_event(event):
            valueStr.set('%.2f' % (value.get(),))
            self.setPoint = value.get()

        tk.Label(frame, textvariable=valueStr).place(x=280, y=10, width=100)
        slider = ttk.Scale(frame, from_=0, to=1, orient='horizontal', command=chose_event, variable=value)
        slider.place(x=105, y=10, width=170)

        def send(event):
            self.setPoint = value.get()
            
        #slider.bind("<ButtonRelease-1>", send)

if __name__ == '__main__':
    pid = PID()
    Thread(target=pid.listenTcp).start()
    pid.ui()
        
