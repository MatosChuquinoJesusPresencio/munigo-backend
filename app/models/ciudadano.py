from sqlmodel import SQLModel, Field

from app.core.config import TipoDocumento


class Ciudadano(SQLModel, table=True):
    __tablename__ = "ciudadanos"

    id: int | None = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuarios.id")
    tipo_documento: TipoDocumento
    numero_documento: str
    nombres_razon_social: str
    telefono: str
    direccion: str
