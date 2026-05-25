from datetime import datetime
from pydantic import BaseModel


class NotificacionBase(BaseModel):
    tipo: str
    mensaje: str


class NotificacionCreate(NotificacionBase):
    id_ciudadano: int
    id_expediente: int | None = None


class NotificacionUpdate(BaseModel):
    leido: bool


class NotificacionResponse(NotificacionBase):
    id: int
    id_ciudadano: int
    id_expediente: int | None
    leido: bool
    fecha_envio: datetime

    class Config:
        from_attributes = True


class NotificacionLeidaRequest(BaseModel):
    leido: bool = True


class NotificacionListaResponse(BaseModel):
    total: int
    no_leidas: int
    notificaciones: list[NotificacionResponse]
