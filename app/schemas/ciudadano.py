from pydantic import BaseModel

from app.core.config import TipoDocumento


class CiudadanoBase(BaseModel):
    tipo_documento: TipoDocumento
    numero_documento: str
    nombres_razon_social: str
    telefono: str
    direccion: str


class CiudadanoCreate(CiudadanoBase):
    pass


class CiudadanoUpdate(BaseModel):
    tipo_documento: TipoDocumento | None = None
    numero_documento: str | None = None
    nombres_razon_social: str | None = None
    telefono: str | None = None
    direccion: str | None = None


class CiudadanoResponse(CiudadanoBase):
    id: int
    id_usuario: int

    class Config:
        from_attributes = True


class CiudadanoCompletoResponse(CiudadanoResponse):
    correo_electronico: str | None = None
