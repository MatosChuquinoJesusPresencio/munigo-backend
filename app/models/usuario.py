from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

from app.core.config import RolUsuario


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    correo_electronico: str = Field(unique=True)
    contrasena: str
    rol: RolUsuario
    fecha_creacion: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    activo: bool = Field(default=True)
