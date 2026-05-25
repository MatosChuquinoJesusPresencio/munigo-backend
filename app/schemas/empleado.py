from pydantic import BaseModel

from app.core.config import RolUsuario


class EmpleadoBase(BaseModel):
    nombres: str
    apellidos: str
    cargo: str
    area: str


class EmpleadoCreate(EmpleadoBase):
    id_usuario: int


class EmpleadoUpdate(BaseModel):
    nombres: str | None = None
    apellidos: str | None = None
    cargo: str | None = None
    area: str | None = None


class EmpleadoResponse(EmpleadoBase):
    id: int
    id_usuario: int

    class Config:
        from_attributes = True


class EmpleadoRolResponse(BaseModel):
    id: int
    id_usuario: int
    nombres: str
    apellidos: str
    cargo: str
    area: str
    rol: RolUsuario | None = None

    class Config:
        from_attributes = True
