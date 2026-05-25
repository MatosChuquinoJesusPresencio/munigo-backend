from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

from app.core.config import EstadoValidacion


class DocumentoAdjunto(SQLModel, table=True):
    __tablename__ = "documentos_adjuntos"

    id: int | None = Field(default=None, primary_key=True)
    id_expediente: int = Field(foreign_key="expedientes.id")
    id_requisito: int | None = Field(default=None, foreign_key="requisitos.id")
    nombre_archivo: str
    ruta_archivo: str
    estado_validacion: EstadoValidacion = Field(default=EstadoValidacion.PENDIENTE)
    observaciones: str = ""
    fecha_subida: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
