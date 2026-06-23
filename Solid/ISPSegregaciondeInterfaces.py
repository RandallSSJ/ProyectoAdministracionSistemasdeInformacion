#El Principio de Segregación de Interfaces se refleja en el uso de interfaces específicas 
# que contienen únicamente los métodos necesarios para cada componente. 
# En el proyecto, los módulos que consultan información sísmica solo dependen de operaciones relacionadas 
# con la obtención de datos y no están obligados a implementar funcionalidades que no utilizan. 
# Esto reduce el acoplamiento entre componentes y permite que cada clase implemente únicamente las responsabilidades que realmente necesita.


from abc import ABC, abstractmethod

class ConsultaSismos(ABC):

    @abstractmethod
    def obtener_sismos(self):
        pass


class ExportacionSismos(ABC):

    @abstractmethod
    def exportar_csv(self):
        pass