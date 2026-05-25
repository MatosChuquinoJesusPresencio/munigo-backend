from datetime import datetime
from pydantic import BaseModel

from app.core.config import EstadoValidacion


class DocumentoAdjuntoBase(BaseModel):
    id_requisito: int | None = None
    nombre_archivo: str
    ruta_archivo: str


class DocumentoAdjuntoCreate(DocumentoAdjuntoBase):
    id_expediente: int


class DocumentoAdjuntoUpdate(BaseModel):
    estado_validacion: EstadoValidacion | None = None
    observaciones: str | None = None


class DocumentoAdjuntoResponse(DocumentoAdjuntoBase):
    id: int
    id_expediente: int
    estado_validacion: EstadoValidacion
    observaciones: str
    fecha_subida: datetime

    class Config:
        from_attributes = True


class DocumentoValidacionRequest(BaseModel):
    id_documento: int
    estado_validacion: EstadoValidacion
    observaciones: str = ""


class DocumentoSubidoResponse(BaseModel):
    id: int
    nombre_archivo: str
    estado_validacion: EstadoValidacion
    mensaje: str
