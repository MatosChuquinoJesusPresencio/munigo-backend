from typing import Optional, List

from sqlmodel import Session, select

from app.models import Expediente
from app.schemas import ExpedienteCreate, ExpedienteUpdate
from app.core.config import EstadoTramite, NivelRiesgo
from app.utils import BaseRepository


class ExpedienteRepository(BaseRepository[Expediente, ExpedienteCreate, ExpedienteUpdate]):
    def __init__(self):
        super().__init__(Expediente)

    def get_by_codigo_seguimiento(
        self,
        session: Session,
        codigo: str
    ) -> Optional[Expediente]:
        statement = select(Expediente).where(Expediente.codigo_seguimiento == codigo)
        results = session.exec(statement)
        return results.first()

    def get_by_ciudadano_id(
        self,
        session: Session,
        ciudadano_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expediente]:
        statement = (
            select(Expediente)
            .where(Expediente.id_ciudadano == ciudadano_id)
            .order_by(Expediente.fecha_ingreso.desc())
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_estado(
        self,
        session: Session,
        estado: EstadoTramite,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expediente]:
        statement = (
            select(Expediente)
            .where(Expediente.estado == estado)
            .order_by(Expediente.fecha_ingreso)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_nivel_riesgo(
        self,
        session: Session,
        nivel_riesgo: NivelRiesgo,
        skip: int = 0,
        limit: int = 100
    ) -> List[Expediente]:
        statement = (
            select(Expediente)
            .where(Expediente.nivel_riesgo == nivel_riesgo)
            .order_by(Expediente.fecha_ingreso)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def update_estado(
        self,
        session: Session,
        id: int,
        nuevo_estado: EstadoTramite
    ) -> Optional[Expediente]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        db_obj.estado = nuevo_estado
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


expediente_repository = ExpedienteRepository()
