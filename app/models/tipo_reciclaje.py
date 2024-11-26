from pydantic import BaseModel
from typing import Optional

class TipoReciclaje(BaseModel):
    id_tipo_reciclaje: Optional[int] = None
    nombre: str
    caracteristicas: str
    puntos_botella: int

    class Config:
        from_attributes = True 