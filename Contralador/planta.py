import numpy as np
from control.matlab import *
from threading import Thread
from time import time

import  tkinter as tk
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
		A = np.pi*r**2
		alfa = 0.5*Ca*rho*A/m
		va_e = np.sqrt(g/alfa) 
		k_m = 0.5 
		tal = 0.01
		Gb = (2*alfa*va_e)/(s**2) #Ft do movimento da bolinha
		Gv = k_m/(tal*s+1) #Ft da ventoinha 
		G = Gv * Gb
		Gs = tf2ss(G)
		self.A = Gs.A
		self.B = Gs.B
		self.h = 1e-4
		self.uk = np.array([0])
		self.xk = np.array([[0],[0],[0]])
		self.data = []
		

	def x_dot(self, t,x,u):
		A =self.A
		B = self.B
		xkp1 = A @ x + B @ u
		return xkp1
	
	def rk4(self, tk,xk,uk):
		h  =  self.h
		xk = xk.reshape([2,1])
		uk = uk.reshape([1,1])
		k1 = x_dot(tk,xk,uk)
		k2 = x_dot(tk+h/2.0,xk+h*k1/2.0,uk)
		k3 = x_dot(tk+h/2.0,xk+h*k2/2.0,uk)
		k4 = x_dot(tk+h,xk+h*k3,uk)
		xkp1 = xk + (h/6.0)*(k1 + 2.0*k2 + 2.0*k3 + k4)
		return xkp1.reshape([2,])
	def  __call__(self):
		t = 0
		while True:
			self.xk = self.rk4(t,self.xk,self.uk)
			self.data.append((t,self.uk[0]))
			t += self.h
			time.sleep(self.h)
	def listenTCP(self):
		pass
	def ui(self):
		uiconf = {}
		root = tk.Tk()
		frame = tk.Frame(root,bg = '#0f0')
		frame.pack(side=tk.LEFT,fill=tk.Y)
		l = 150
		canvas = tk.Canvas(frame,scrollregion=(-2*l,-l, 2*l, l))
		canvas.pack(fill = tk.Y,expand=True)
		uiconf['frame:size'] = (int(root.winfo_width()),int(root.winfo_height()))
		uiconf['frame:init'] = True
		
		
		def resize(event):
			# canvas.xview_scroll(-uiconf['frame:size'][0]//2,'units')
			# canvas.yview_scroll(uiconf['frame:size'][1]//2,'units')
			print(uiconf['frame:size'])
			uiconf['frame:size'] =  (int(root.winfo_width()),int(root.winfo_height()))
			if uiconf['frame:init']:
				print(uiconf['frame:size'])
				canvas.xview_scroll(uiconf['frame:size'][0]//20,'units')
				canvas.yview_scroll(-uiconf['frame:size'][1]//20,'units')
			uiconf['frame:init'] = True
		root.bind("<Configure>", resize)
		canvas.create_rectangle(0,0,100,100,fill = '#f00')

		root.mainloop()
		
l = Levitador()
print('runing')
l.ui()
print('end')