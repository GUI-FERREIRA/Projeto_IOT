"""
Objeto responsavel pela comunicao entre o 
servidor flask com o arduino

Comunicao  do tipo Serial

dependências:
pip install pyserial

"""
from threading import Thread

from serial import Serial
from serial.tools.list_ports import comports

PLUGS = 1
STATUS = 2

def defaultHandle(msg):
    pass


class Bridge:
    def __init__(self):
        self.serial = None
        self.run = True
        self._handleReceive = defaultHandle
        self._handleListener = None
        self.handleWait = 100 # tempo a cada verificação
    def send(self, string):
        pass

    def setReceiveListener(self, listener):
        self._handleReceive = listener

    def getPortsAvalaible(self):
        # retorna as portas que nao estao abertas
        portas = comports()
        pt = []
        for d in portas:
            s = Serial(d.device)
            if not s.isOpen():
                pt.append(d.device)
        return pt

    def connect(self, port, speed=9600):
        if not (self.serial is None):
            return False, 'Porta ja está conectada'
        # conecta a uma porta contida nas portas disponiveis
        if not port in self.getPortsAvalaible():
            return False, 'Porta indisponivel'
        self.serial = Serial(port, speed)
        self.serial.open()
        def f():
            while self.run and self.serial.isOpen():
                serial = Serial()
                n = serial.read(size=4)
                n = int.from_bytes(n, byteorder='big', signed=True)
                msg = serial.read(size=n)
                self._handleReceive(msg)
        self._handleListener = Thread(target = f)
        return True, ''

    def __del__(self):
        self.run = False
        if not (self.serial is None) and self.serial.isOpen():
            self.serial.close()


b = Bridge()
print(b.getPortsAvalaible())
