from pydantic import BaseModel
from typing import Optional

class Ranking(BaseModel):
    id_ranking: Optional[int] = None
    id_usuario: int
    id_reciclaje: int
    id_evento: int
    id_premio: Optional[int] = None
    puntaje_total: int
    posicion: int

    class Config:
        from_attributes = True 