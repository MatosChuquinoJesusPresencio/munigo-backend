from datetime import date, time, datetime
from pydantic import BaseModel

from app.core.config import EstadoCita


class CitaBase(BaseModel):
    fecha: date
    hora_inicio: time
    hora_fin: time


class CitaCreate(CitaBase):
    id_expediente: int
    id_funcionario: int | None = None


class CitaUpdate(BaseModel):
    fecha: date | None = None
    hora_inicio: time | None = None
    hora_fin: time | None = None
    estado: EstadoCita | None = None
    id_funcionario: int | None = None


class CitaEstadoUpdate(BaseModel):
    estado: EstadoCita


class CitaResponse(CitaBase):
    id: int
    id_expediente: int
    id_funcionario: int | None
    estado: EstadoCita

    class Config:
        from_attributes = True


class CitaDisponibilidadRequest(BaseModel):
    fecha: date


class CitaDisponibilidadResponse(BaseModel):
    fecha: date
    horarios_disponibles: list[dict[str, time]]


class CitaAsignarRequest(BaseModel):
    id_expediente: int
    fecha: date
    hora_inicio: time
    hora_fin: time
