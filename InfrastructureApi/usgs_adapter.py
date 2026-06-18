import requests

from Ports.repositorio_sismos import RepositorioSismos

from Domain.exceptions import ApiCaidaError


class USGSAdapter(RepositorioSismos):

    def obtener_sismos(self):

        try:

            url = (
                "https://earthquake.usgs.gov/fdsnws/event/1/query"
                "?format=geojson"
                "&limit=20"
            )

            respuesta = requests.get(
                url,
                timeout=10
            )

            respuesta.raise_for_status()

            return respuesta.json()

        except Exception:

            raise ApiCaidaError(
                "No fue posible conectar con la API"
            )