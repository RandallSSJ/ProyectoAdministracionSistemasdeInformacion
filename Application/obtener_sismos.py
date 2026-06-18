from Domain.exceptions import ApiCaidaError


class ObtenerSismos:

    def __init__(self, repositorio):

        self.repositorio = repositorio

    def ejecutar(self):

        return self.repositorio.obtener_sismos()