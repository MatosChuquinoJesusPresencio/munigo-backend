from datetime import datetime, timezone
from sqlmodel import SQLModel, Field


class Notificacion(SQLModel, table=True):
    __tablename__ = "notificaciones"

    id: int | None = Field(default=None, primary_key=True)
    id_ciudadano: int = Field(foreign_key="ciudadanos.id")
    id_expediente: int | None = Field(default=None, foreign_key="expedientes.id")
    tipo: str
    mensaje: str
    leido: bool = Field(default=False)
    fecha_envio: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
