from bridge import *


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
        self._on_request = on_request_success

    def __check_request__(self, request, obj):
        if request == PLUGS:
            gpio_free = [gpio for gpio in obj if not (gpio in self.tomadas)]
            self._on_request(request, gpio_free)
            return
        if request == STATUS:
            for _, tomada in self.tomadas.items():
                tomada.status = obj[tomada.gpio]
            self._on_request(request, True)
            return

    def get_serial(self):
        return self.ponte.getPortsAvalaible()

    def arduino_conect(self, port, serial_speed=9600):
        self.arduino_conected, erro = self.ponte.connect(port, serial_speed)
        return self.arduino_conected, erro

    def get_plug(self):  # Retorna as tomadas disponíveis no arduino
        self.ponte.request(PLUGS, self.__check_request__)

    def change_plug(self, gpio, new_status):
        if gpio in self.tomadas:
            self.tomadas[gpio].status = new_status
            self.ponte.change_plug(gpio, new_status)
            return True
        return False

    def registerPlug(self, name, gpio):
    	self.tomadas[gpio].name = name

    def delete(self, gpio):
    	pass



if __name__ == '__main__':
    manager = Manager()
    print(manager.get_serial())
