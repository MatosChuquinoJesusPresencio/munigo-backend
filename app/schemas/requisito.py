from pydantic import BaseModel

from app.core.config import TipoTramite


class RequisitoBase(BaseModel):
    nombre: str
    descripcion: str = ""
    tipo_archivo_permitido: str = "pdf,jpg,jpeg,png"
    es_obligatorio: bool = True
    aplica_a: TipoTramite | None = None


class RequisitoCreate(RequisitoBase):
    pass


class RequisitoUpdate(BaseModel):
    nombre: str | None = None
    descripcion: str | None = None
    tipo_archivo_permitido: str | None = None
    es_obligatorio: bool | None = None
    aplica_a: TipoTramite | None = None


class RequisitoResponse(RequisitoBase):
    id: int

    class Config:
        from_attributes = True


class RequisitoListaRequest(BaseModel):
    tipo_tramite: TipoTramite
    nivel_riesgo: str = "todos"


class RequisitoListaResponse(BaseModel):
    tipo_tramite: TipoTramite
    requisitos: list[RequisitoResponse]


class TramiteRequisitoBase(BaseModel):
    id_requisito: int
    cumplido: bool = False


class TramiteRequisitoCreate(TramiteRequisitoBase):
    id_expediente: int
    id_documento: int | None = None


class TramiteRequisitoResponse(TramiteRequisitoBase):
    id: int
    id_expediente: int
    id_documento: int | None

    class Config:
        from_attributes = True
