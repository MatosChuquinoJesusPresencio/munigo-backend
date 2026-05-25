from typing import Optional, List

from sqlmodel import Session, select

from app.models import TramiteRequisito
from app.schemas import TramiteRequisitoCreate, TramiteRequisitoBase
from app.utils import BaseRepository


class TramiteRequisitoRepository(BaseRepository[TramiteRequisito, TramiteRequisitoCreate, TramiteRequisitoBase]):
    def __init__(self):
        super().__init__(TramiteRequisito)

    def get_by_expediente_id(
        self,
        session: Session,
        expediente_id: int
    ) -> List[TramiteRequisito]:
        statement = (
            select(TramiteRequisito)
            .where(TramiteRequisito.id_expediente == expediente_id)
            .order_by(TramiteRequisito.id)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_requisito_id(
        self,
        session: Session,
        requisito_id: int
    ) -> List[TramiteRequisito]:
        statement = select(TramiteRequisito).where(TramiteRequisito.id_requisito == requisito_id)
        results = session.exec(statement)
        return list(results.all())

    def get_cumplidos(
        self,
        session: Session,
        expediente_id: int
    ) -> List[TramiteRequisito]:
        statement = (
            select(TramiteRequisito)
            .where(TramiteRequisito.id_expediente == expediente_id)
            .where(TramiteRequisito.cumplido == True)
            .order_by(TramiteRequisito.id)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_pendientes(
        self,
        session: Session,
        expediente_id: int
    ) -> List[TramiteRequisito]:
        statement = (
            select(TramiteRequisito)
            .where(TramiteRequisito.id_expediente == expediente_id)
            .where(TramiteRequisito.cumplido == False)
            .order_by(TramiteRequisito.id)
        )
        results = session.exec(statement)
        return list(results.all())

    def marcar_cumplido(
        self,
        session: Session,
        id: int,
        id_documento: int | None = None
    ) -> Optional[TramiteRequisito]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        db_obj.cumplido = True
        if id_documento:
            db_obj.id_documento = id_documento
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def verificar_todos_cumplidos(
        self,
        session: Session,
        expediente_id: int
    ) -> bool:
        from sqlmodel import func
        statement_total = (
            select(func.count())
            .select_from(TramiteRequisito)
            .where(TramiteRequisito.id_expediente == expediente_id)
        )
        total = session.exec(statement_total).one()
        
        statement_cumplidos = (
            select(func.count())
            .select_from(TramiteRequisito)
            .where(TramiteRequisito.id_expediente == expediente_id)
            .where(TramiteRequisito.cumplido == True)
        )
        cumplidos = session.exec(statement_cumplidos).one()
        
        return total == cumplidos


tramite_requisito_repository = TramiteRequisitoRepository()
