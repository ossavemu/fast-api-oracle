from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    documento: str
    telefono: str
    nombre: str
    apellido: str
    correo: EmailStr
    contrasena: str

class UserLogin(BaseModel):
    correo: EmailStr
    contrasena: str

class User(BaseModel):
    id_usuario: int
    documento: str
    telefono: str
    nombre: str
    apellido: str
    correo: EmailStr
    id_perfil: int = 1  # 1: usuario normal, 2: admin

    class Config:
        from_attributes = True 