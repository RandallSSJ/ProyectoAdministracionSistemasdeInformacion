#El Principio Abierto/Cerrado se aplica porque el sistema puede ampliarse sin necesidad de modificar el código existente.
# Por ejemplo, si en el futuro se desea obtener información sísmica desde una nueva fuente de datos o una base de datos diferente 
# basta con crear una nueva implementación del repositorio respetando la misma interfaz. 
# De esta forma se agregan nuevas funcionalidades sin alterar el funcionamiento de las clases ya desarrolladas.



from abc import ABC, abstractmethod

class FuenteSismos(ABC):

    @abstractmethod
    def obtener(self):
        pass


class ApiUSGS(FuenteSismos):

    def obtener(self):
        return "Datos USGS"


class ApiLocal(FuenteSismos):

    def obtener(self):
        return "Datos locales"