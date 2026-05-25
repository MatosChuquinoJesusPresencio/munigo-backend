from datetime import datetime
from pydantic import BaseModel

from app.core.config import EstadoTramite, NivelRiesgo, TipoTramite


class ExpedienteBase(BaseModel):
    tipo_tramite: TipoTramite
    giro: str
    tamano_local: int
    direccion_local: str = ""
    zona: str = ""


class ExpedienteCreate(ExpedienteBase):
    pass


class ExpedienteUpdate(BaseModel):
    tipo_tramite: TipoTramite | None = None
    nivel_riesgo: NivelRiesgo | None = None
    giro: str | None = None
    tamano_local: int | None = None
    direccion_local: str | None = None
    zona: str | None = None
    estado: EstadoTramite | None = None


class ExpedienteEstadoUpdate(BaseModel):
    estado: EstadoTramite


class ExpedienteResponse(ExpedienteBase):
    id: int
    id_ciudadano: int
    nivel_riesgo: NivelRiesgo
    codigo_seguimiento: str
    estado: EstadoTramite
    fecha_ingreso: datetime

    class Config:
        from_attributes = True


class ExpedienteRiesgoRequest(BaseModel):
    tipo_tramite: TipoTramite
    giro: str
    tamano_local: int


class ExpedienteRiesgoResponse(BaseModel):
    nivel_riesgo: NivelRiesgo
    requiere_inspeccion: bool
    motivo: str
