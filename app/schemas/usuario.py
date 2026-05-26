from datetime import datetime
from pydantic import BaseModel, EmailStr

from app.core.config import RolUsuario


class UsuarioBase(BaseModel):
    correo_electronico: EmailStr


class UsuarioCreate(UsuarioBase):
    contrasena: str


class UsuarioLogin(BaseModel):
    correo_electronico: EmailStr
    contrasena: str


class UsuarioUpdate(BaseModel):
    correo_electronico: EmailStr | None = None
    activo: bool | None = None


class UsuarioResponse(UsuarioBase):
    id: int
    rol: RolUsuario
    fecha_creacion: datetime
    activo: bool

    class Config:
        from_attributes = True


class UsuarioRolResponse(BaseModel):
    id: int
    rol: RolUsuario

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
    email: str | None = None
    role: RolUsuario | None = None


from app.core.config import TipoDocumento

class RegistroRequest(BaseModel):
    correo_electronico: EmailStr
    contrasena: str
    tipo_documento: TipoDocumento
    numero_documento: str
    nombres_razon_social: str
    telefono: str
    direccion: str = ""
