from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

from app.core.config import EstadoTramite, NivelRiesgo, TipoTramite


class Expediente(SQLModel, table=True):
    __tablename__ = "expedientes"

    id: int | None = Field(default=None, primary_key=True)
    id_ciudadano: int = Field(foreign_key="ciudadanos.id")
    tipo_tramite: TipoTramite
    nivel_riesgo: NivelRiesgo = Field(default=NivelRiesgo.BAJO)
    codigo_seguimiento: str = Field(unique=True)
    giro: str
    tamano_local: int
    direccion_local: str = ""
    zona: str = ""
    estado: EstadoTramite = Field(default=EstadoTramite.BORRADOR)
    fecha_ingreso: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
