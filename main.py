from InfrastructureApi.usgs_adapter import USGSAdapter
from InfrastructureDataBase.sqlite_adapter import SQLiteAdapter
from Application.obtener_sismos import ObtenerSismos
from Domain.exceptions import ApiCaidaError


def crear_servicio():

    try:

        repo = USGSAdapter()

        repo.obtener_sismos()

        return ObtenerSismos(repo)

    except ApiCaidaError:

        repo = SQLiteAdapter()

        return ObtenerSismos(repo)