from abc import ABC, abstractmethod

class RepositorioSismos(ABC):

    @abstractmethod
    def obtener_sismos(self):
        pass