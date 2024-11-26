from pydantic import BaseModel
from typing import Optional

class Bono(BaseModel):
    id_bono: Optional[int] = None
    id_evento: int
    descripcion: str
    valor_puntos: int

    class Config:
        from_attributes = True 