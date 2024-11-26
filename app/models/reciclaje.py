from pydantic import BaseModel
from typing import Optional

class Reciclaje(BaseModel):
    id_reciclaje: Optional[int] = None
    id_evento: int
    id_usuario: int
    cantidad: int
    puntos: int
    puntos_bono: int
    puntos_totales: int

    class Config:
        from_attributes = True 