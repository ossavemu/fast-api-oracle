from pydantic import BaseModel
from typing import Optional

class Premio(BaseModel):
    id_premio: Optional[int] = None
    id_evento: int
    descripcion_premio: str

    class Config:
        from_attributes = True 