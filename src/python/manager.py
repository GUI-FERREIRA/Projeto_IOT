from bridge import *
import pickle


class Tomada:
    def __init__(self, nome, gpio, status):
        self.nome = nome
        self.gpio = gpio
        self.status = status


def on_request_success(request, obj):
    pass


class Manager:
    def __init__(self):
        self.arduino_conected = False
        self.tomadas = {}
        self.ponte = Bridge()
        self.ponte.setReceiveListener(self.__check_request__)
        self._on_request = on_request_success
        self.load()
        self.pins = {}

    def hasArduinoConnected(self):
        return self.arduino_conected

    def updateTomadas(self):
        for _, tomada in self.tomadas.items():
            tomada.status = self.pins[tomada.gpio]

    def __check_request__(self, request, obj):
        if request == PLUGS:  ## obsoleto
            gpio_free = [gpio for gpio in obj if not (gpio in self.tomadas)]
            self._on_request(request, gpio_free)
            return
        if request == STATUS:
            self.pins = obj
            for _, tomada in self.tomadas.items():
                tomada.status = obj[tomada.gpio]
            if self._on_request != None:
                self._on_request(request, True)
            return

    def get_serial(self):
        return self.ponte.getPortsAvalaible()

    def arduino_conect(self, port, serial_speed=9600):
        self.arduino_conected, erro = self.ponte.connect(port, serial_speed)
        self.ponte.request(STATUS)
        return self.arduino_conected, erro

    def getAvailablePlug(self):
        a = list(self.pins.keys())
        b = list(self.tomadas.keys())
        return [c for c in a if not (a in b)]

    def setRequestListener(self, handleListener):
        self.on_request_success = handleListener

    def change_plug(self, gpio, new_status):
        gpio = int(gpio)
        if gpio in self.tomadas:
            self.tomadas[gpio].status = new_status
            self.pins[gpio] = new_status
            self.ponte.change_plug(gpio, new_status)
            return True
        return False

    def get_tomada(self):  # Retorna lista das gpio utilizadas
        plugs = [value for key, value in self.tomadas.items()]
        return plugs

    def registerPlug(self, name, gpio):
        gpio = int(gpio)
        if gpio in self.tomadas:
            self.tomadas[gpio].name = name
        else:
            self.tomadas[gpio] = Tomada(name,gpio,self.pins[gpio])
        self.save()
        return True

    def inverte(self, gpio):
        if gpio in self.tomadas:
            self.change_plug(gpio, not self.tomadas[gpio].status)
            return True
        return False

    def delete_plug(self, gpio):
        gpio = int(gpio)
        if gpio in self.tomadas:
            del self.tomadas[gpio]
            self.save()
            return True
        return False

    def save(self):
        with open('.registro.p', 'wb') as f:
            pickle.dump(self.tomadas, f)
        f.close()

    def load(self):
        try:
            with open('.registro.p', 'rb') as f:
                self.tomadas = pickle.load(f)
            f.close()
        except Exception:
            pass


if __name__ == '__main__':
    manager = Manager()
    manager.load()
    print(manager.get_serial())
