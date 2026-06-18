from dataclasses import dataclass

@dataclass
class Sismo:

    id_sismo: str
    fecha: str
    magnitud: float
    profundidad: float
    lugar: str