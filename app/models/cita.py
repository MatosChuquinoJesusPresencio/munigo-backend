from datetime import date, time
from sqlmodel import SQLModel, Field

from app.core.config import EstadoCita


class Cita(SQLModel, table=True):
    __tablename__ = "citas"

    id: int | None = Field(default=None, primary_key=True)
    id_expediente: int = Field(foreign_key="expedientes.id")
    id_funcionario: int | None = Field(default=None, foreign_key="empleados.id")
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: EstadoCita = Field(default=EstadoCita.PROGRAMADA)
