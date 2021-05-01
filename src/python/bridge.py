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
SET = 3




class Bridge:
    def __init__(self):
        self.serial = None
        self.run = True
        self.__handleReceive = None
        self._handleListener = None
        self.handleWait = 100  # tempo a cada verificação

    def setReceiveListener(self, listener):
        self.__handleReceive = listener

    def getPortsAvalaible(self):
        # retorna as portas que nao estao abertas
        portas = comports()
        return [d.device for d in portas]

    def connect(self, port, speed=9600):
        if not (self.serial is None):
            return False, 'Porta ja está conectada'
        if self.__handleReceive is None:
            return False, 'call back nao atribuido'
        # conecta a uma porta contida nas portas disponiveis
        if not port in self.getPortsAvalaible():
            return False, 'Porta indisponivel'
        self.serial = Serial(port, speed)
        self.serial.open()

        def f():
            while self.run and self.serial.isOpen():
                # o primeiro byte corresponde ao numero de bytes subsequentes
                # o segundo byte corresponde ao numero de agrupamento, caso seja diferente de 1 sera na forma de um dicionario
                # os proximos bytes corresponde ao valor de retorno

                nbytes = self.serial.read(size=1)
                n = int.from_bytes(nbytes, byteorder='big', signed=True)
                data = list(self.serial.read(size=n))
                command = data.pop(0)
                agp = data.pop(0)
                if agp == 1 :
                    self.__handleReceive(command, data)
                    continue
                obj = {data[i]: data[i + 1:i + agp] for i in range(0, len(data), agp)}
                self.__handleReceive(command, obj)

        self._handleListener = Thread(target=f)
        return True, ''

    def __del__(self):
        self.run = False
        if not (self.serial is None) and self.serial.isOpen():
            self.serial.close()

    def change_plug(self, gpio, new_status):
        # o primeiro byte corresponde ao numero de bytes a ser enviados
        # o segundo byte enviado corresponde ao commando SET
        # o terceiro byte corresponde a gpio destino
        # o quarto byte é o novo estado 1 ou 0
        command = SET.to_bytes(length=1, byteorder='big', signed=False)
        gpio = gpio.to_bytes(length=1, byteorder='big', signed=False)
        state = new_status.to_bytes(length=1, byteorder='big', signed=False)
        msg = command + gpio + state
        length = len(msg).to_bytes(length=1, byteorder='big', signed=False)
        self.serial.write(length + msg)

    def request(self, req):
        # o primeiro byte corresponde ao numero de bytes a ser enviados
        # o segundo byte enviado corresponde ao commando req
        if req == SET:
            raise AttributeError("O request SET nao esta disponivel")
        command = req.to_bytes(length=1, byteorder='big', signed=False)
        msg = command
        length = len(msg).to_bytes(length=1, byteorder='big', signed=False)
        self.serial.write(length + msg)


if __name__ == '__main__':
    b = Bridge()
    print(b.getPortsAvalaible())
