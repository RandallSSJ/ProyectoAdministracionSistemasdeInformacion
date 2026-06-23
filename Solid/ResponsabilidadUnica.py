#En este proyecto de monitoreo de sismos se aplica el Principio de Responsabilidad Única 
# porque cada componente tiene una función específica dentro del sistema. 
# Por ejemplo, el repositorio se encarga únicamente de obtener los datos de los sismos desde la API, 
# el caso de uso procesa la información obtenida y la interfaz de Streamlit se limita a mostrar los datos al usuario. 
# Esta separación permite que los cambios realizados en una parte del sistema no afecten directamente a las demás 
# facilitando el mantenimiento y la comprensión del código.


class Sismo:
    def _init_(self, lugar, magnitud):
        self.lugar = lugar
        self.magnitud = magnitud


class SismoRepository:
    def obtener_sismos(self):
        return []