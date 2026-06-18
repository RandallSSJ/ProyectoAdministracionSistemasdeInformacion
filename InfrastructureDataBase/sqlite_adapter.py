import sqlite3

from Ports.repositorio_sismos import RepositorioSismos


class SQLiteAdapter(RepositorioSismos):

    def obtener_sismos(self):

        conexion = sqlite3.connect(
            "sismos_nicaragua.db"
        )

        cursor = conexion.cursor()

        cursor.execute("""
        SELECT
            id_sismo,
            fecha,
            magnitud,
            profundidad
        FROM sismos
        LIMIT 20
        """)

        datos = cursor.fetchall()

        conexion.close()

        return datos