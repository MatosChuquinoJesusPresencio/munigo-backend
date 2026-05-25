from sqlmodel import SQLModel, Field


class TramiteRequisito(SQLModel, table=True):
    __tablename__ = "tramites_requisitos"

    id: int | None = Field(default=None, primary_key=True)
    id_expediente: int = Field(foreign_key="expedientes.id")
    id_requisito: int = Field(foreign_key="requisitos.id")
    id_documento: int | None = Field(default=None, foreign_key="documentos_adjuntos.id")
    cumplido: bool = Field(default=False)
