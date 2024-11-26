from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Evento(BaseModel):
    id_evento: Optional[int] = None
    id_usuario: int
    id_tipo_reciclaje: int
    nombre: str
    lugar: str
    h_inicio: datetime
    h_final: datetime
    fecha: datetime
    observaciones: Optional[str] = None

    class Config:
        from_attributes = True 