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
    
    def hasArduinoConnected(self):
    	return self.arduino_conected


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

    def get_AvaliablePlug(self):  # Retorna as tomadas disponíveis no arduino
        self.ponte.request(PLUGS)

    def setRequestListener(self, handleListener):
    	self.on_request_success = handleListener

    def change_plug(self, gpio, new_status):
        if gpio in self.tomadas:
            self.tomadas[gpio].status = new_status
            self.ponte.change_plug(gpio, new_status)
            return True
        return False

    def get_tomada(self): # Retorna lista das gpio utilizadas
    	plugs = [value for key, value in self.tomadas.items()]
    	return plugs

    def registerPlug(self, name, gpio):
    	if gpio in self.tomadas:
    		self.tomadas[gpio].name = name
    		self.save()
    		return True
    	return False

    def delete_plug(self, gpio):
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
    	with open('.registro.p', 'rb') as f:
    		self.tomadas = pickle.load(f)
    	f.close()
    	
if __name__ == '__main__':
    manager = Manager()
    print(manager.get_serial())
