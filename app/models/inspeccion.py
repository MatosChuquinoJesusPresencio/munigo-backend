from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

from app.core.config import ResultadoInspeccion


class Inspeccion(SQLModel, table=True):
    __tablename__ = "inspecciones"

    id: int | None = Field(default=None, primary_key=True)
    id_expediente: int = Field(foreign_key="expedientes.id")
    id_inspector: int = Field(foreign_key="empleados.id")
    resultado: ResultadoInspeccion = Field(default=ResultadoInspeccion.PENDIENTE)
    comentarios: str = ""
    foto_ruta: str = ""
    fecha_programada: datetime | None = None
    fecha_ejecucion: datetime | None = None
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
