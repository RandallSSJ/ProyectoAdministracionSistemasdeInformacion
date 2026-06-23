#El Principio de Sustitución de Liskov se cumple porque cualquier implementación de un repositorio de sismos 
# puede sustituir a otra sin afectar el comportamiento del sistema. 
# Por ejemplo, el caso de uso puede trabajar indistintamente con un repositorio que obtenga datos desde una API externa 
# o con uno que consulte una base de datos local, siempre que ambos implementen los mismos métodos definidos por la abstracción. 
# Esto garantiza que el sistema mantenga un comportamiento consistente independientemente de la implementación utilizada.









from abc import ABC, abstractmethod

class FuenteSismos(ABC):

    @abstractmethod
    def obtener(self):
        pass


class ApiUSGS(FuenteSismos):

    def obtener(self):
        return []


class ApiLocal(FuenteSismos):

    def obtener(self):
        return []