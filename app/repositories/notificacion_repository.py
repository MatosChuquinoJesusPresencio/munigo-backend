from typing import Optional, List

from sqlmodel import Session, select

from app.models import Notificacion
from app.schemas import NotificacionCreate, NotificacionUpdate
from app.utils import BaseRepository


class NotificacionRepository(BaseRepository[Notificacion, NotificacionCreate, NotificacionUpdate]):
    def __init__(self):
        super().__init__(Notificacion)

    def get_by_ciudadano_id(
        self,
        session: Session,
        ciudadano_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notificacion]:
        statement = (
            select(Notificacion)
            .where(Notificacion.id_ciudadano == ciudadano_id)
            .order_by(Notificacion.fecha_envio.desc())
            .offset(skip)
            .limit(limit)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_expediente_id(
        self,
        session: Session,
        expediente_id: int
    ) -> List[Notificacion]:
        statement = (
            select(Notificacion)
            .where(Notificacion.id_expediente == expediente_id)
            .order_by(Notificacion.fecha_envio.desc())
        )
        results = session.exec(statement)
        return list(results.all())

    def get_no_leidas(
        self,
        session: Session,
        ciudadano_id: int
    ) -> List[Notificacion]:
        statement = (
            select(Notificacion)
            .where(Notificacion.id_ciudadano == ciudadano_id)
            .where(Notificacion.leido == False)
            .order_by(Notificacion.fecha_envio.desc())
        )
        results = session.exec(statement)
        return list(results.all())

    def count_no_leidas(
        self,
        session: Session,
        ciudadano_id: int
    ) -> int:
        from sqlmodel import func
        statement = (
            select(func.count())
            .select_from(Notificacion)
            .where(Notificacion.id_ciudadano == ciudadano_id)
            .where(Notificacion.leido == False)
        )
        result = session.exec(statement)
        return result.one()

    def marcar_leida(
        self,
        session: Session,
        id: int
    ) -> Optional[Notificacion]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        db_obj.leido = True
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def marcar_todas_leidas(
        self,
        session: Session,
        ciudadano_id: int
    ) -> int:
        statement = (
            select(Notificacion)
            .where(Notificacion.id_ciudadano == ciudadano_id)
            .where(Notificacion.leido == False)
        )
        results = session.exec(statement)
        count = 0
        for notificacion in results.all():
            notificacion.leido = True
            session.add(notificacion)
            count += 1
        session.commit()
        return count


notificacion_repository = NotificacionRepository()
