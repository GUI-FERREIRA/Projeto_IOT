import threading
class Atomic():
    def __init__(self, value=0):
        self._value = value
        self._lock = threading.Lock()
    @property
    def value(self):
        with self._lock:
            return self._value

    @value.setter
    def value(self, v):
        with self._lock:
            self._value = v
            return self._value
    def __repr__(self):
        return str(self._value)
    
            
if __name__ == '__main__':
    a = Atomic(3)
    print(a)
    a.value = 4
    print(a)
    b = a.value
    print(b)