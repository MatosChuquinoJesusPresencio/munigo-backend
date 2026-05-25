from datetime import datetime
from pydantic import BaseModel

from app.core.config import ResultadoInspeccion


class InspeccionBase(BaseModel):
    fecha_programada: datetime | None = None


class InspeccionCreate(InspeccionBase):
    id_expediente: int
    id_inspector: int


class InspeccionUpdate(BaseModel):
    fecha_programada: datetime | None = None
    fecha_ejecucion: datetime | None = None
    resultado: ResultadoInspeccion | None = None
    comentarios: str | None = None
    foto_ruta: str | None = None


class InspeccionResultadoRequest(BaseModel):
    resultado: ResultadoInspeccion
    comentarios: str = ""
    foto_ruta: str = ""


class InspeccionResponse(InspeccionBase):
    id: int
    id_expediente: int
    id_inspector: int
    resultado: ResultadoInspeccion
    comentarios: str
    foto_ruta: str
    fecha_ejecucion: datetime | None
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class InspeccionAsignarRequest(BaseModel):
    id_expediente: int
    id_inspector: int
    fecha_programada: datetime | None = None


class HojaRutaItem(BaseModel):
    id_inspeccion: int
    id_expediente: int
    direccion_local: str
    zona: str
    fecha_programada: datetime | None


class HojaRutaResponse(BaseModel):
    inspector_id: int
    inspector_nombre: str
    fecha: datetime
    inspecciones: list[HojaRutaItem]
