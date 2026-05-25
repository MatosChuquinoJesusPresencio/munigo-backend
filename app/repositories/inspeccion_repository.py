from typing import Optional, List
from datetime import datetime

from sqlmodel import Session, select

from app.models import Inspeccion
from app.schemas import InspeccionCreate, InspeccionUpdate
from app.core.config import ResultadoInspeccion
from app.utils import BaseRepository


class InspeccionRepository(BaseRepository[Inspeccion, InspeccionCreate, InspeccionUpdate]):
    def __init__(self):
        super().__init__(Inspeccion)

    def get_by_expediente_id(
        self,
        session: Session,
        expediente_id: int
    ) -> List[Inspeccion]:
        statement = (
            select(Inspeccion)
            .where(Inspeccion.id_expediente == expediente_id)
            .order_by(Inspeccion.fecha_creacion.desc())
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_inspector_id(
        self,
        session: Session,
        inspector_id: int,
        fecha_programada: datetime | None = None
    ) -> List[Inspeccion]:
        statement = select(Inspeccion).where(Inspeccion.id_inspector == inspector_id)
        if fecha_programada:
            statement = statement.where(Inspeccion.fecha_programada == fecha_programada)
        statement = statement.order_by(Inspeccion.fecha_programada)
        results = session.exec(statement)
        return list(results.all())

    def get_by_resultado(
        self,
        session: Session,
        resultado: ResultadoInspeccion,
        skip: int = 0,
        limit: int = 100
    ) -> List[Inspeccion]:
        statement = (
            select(Inspeccion)
            .where(Inspeccion.resultado == resultado)
            .order_by(Inspeccion.fecha_programada)
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_pendientes(
        self,
        session: Session,
        inspector_id: int | None = None
    ) -> List[Inspeccion]:
        statement = select(Inspeccion).where(Inspeccion.resultado == ResultadoInspeccion.PENDIENTE)
        if inspector_id:
            statement = statement.where(Inspeccion.id_inspector == inspector_id)
        statement = statement.order_by(Inspeccion.fecha_programada)
        results = session.exec(statement)
        return list(results.all())

    def update_resultado(
        self,
        session: Session,
        id: int,
        nuevo_resultado: ResultadoInspeccion,
        comentarios: str = "",
        foto_ruta: str = ""
    ) -> Optional[Inspeccion]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        db_obj.resultado = nuevo_resultado
        if comentarios:
            db_obj.comentarios = comentarios
        if foto_ruta:
            db_obj.foto_ruta = foto_ruta
        db_obj.fecha_ejecucion = datetime.now()
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


inspeccion_repository = InspeccionRepository()
