from sqlmodel import SQLModel, Field

from app.core.config import TipoTramite


class Requisito(SQLModel, table=True):
    __tablename__ = "requisitos"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str
    descripcion: str = ""
    tipo_archivo_permitido: str = "pdf,jpg,jpeg,png"
    es_obligatorio: bool = Field(default=True)
    aplica_a: TipoTramite | None = None
