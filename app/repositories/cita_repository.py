from typing import Optional, List
from datetime import date

from sqlmodel import Session, select

from app.models import Cita
from app.schemas import CitaCreate, CitaUpdate
from app.core.config import EstadoCita
from app.utils import BaseRepository


class CitaRepository(BaseRepository[Cita, CitaCreate, CitaUpdate]):
    def __init__(self):
        super().__init__(Cita)

    def get_by_expediente_id(
        self,
        session: Session,
        expediente_id: int
    ) -> List[Cita]:
        statement = (
            select(Cita)
            .where(Cita.id_expediente == expediente_id)
            .order_by(Cita.fecha.desc())
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_funcionario_id(
        self,
        session: Session,
        funcionario_id: int,
        fecha: date | None = None
    ) -> List[Cita]:
        statement = select(Cita).where(Cita.id_funcionario == funcionario_id)
        if fecha:
            statement = statement.where(Cita.fecha == fecha)
        statement = statement.order_by(Cita.fecha, Cita.hora_inicio)
        results = session.exec(statement)
        return list(results.all())

    def get_by_fecha(
        self,
        session: Session,
        fecha: date,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cita]:
        statement = (
            select(Cita)
            .where(Cita.fecha == fecha)
            .order_by(Cita.hora_inicio)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_estado(
        self,
        session: Session,
        estado: EstadoCita,
        skip: int = 0,
        limit: int = 100
    ) -> List[Cita]:
        statement = (
            select(Cita)
            .where(Cita.estado == estado)
            .order_by(Cita.fecha, Cita.hora_inicio)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def update_estado(
        self,
        session: Session,
        id: int,
        nuevo_estado: EstadoCita
    ) -> Optional[Cita]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        db_obj.estado = nuevo_estado
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


cita_repository = CitaRepository()
