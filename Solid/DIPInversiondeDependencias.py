#El Principio de Inversión de Dependencias se aplica porque la lógica principal del sistema depende de abstracciones 
# y no de implementaciones concretas. 
# El caso de uso encargado de consultar los sismos recibe un repositorio mediante inyección de dependencias 
# sin conocer si los datos provienen de una API, una base de datos o cualquier otra fuente. 
# Gracias a esto, los módulos de alto nivel permanecen independientes de los detalles de implementación 
# logrando un diseño más flexible, mantenible y alineado con la arquitectura hexagonal utilizada en el proyecto.


from abc import ABC, abstractmethod

class RepositorioSismos(ABC):

    @abstractmethod
    def obtener_sismos(self):
        pass


class ApiRepositorio(RepositorioSismos):

    def obtener_sismos(self):
        return []


class ConsultarSismos:

    def _init_(self, repositorio: RepositorioSismos):
        self.repositorio = repositorio

    def ejecutar(self):
        return self.repositorio.obtener_sismos()