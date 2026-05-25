from typing import Optional, List

from sqlmodel import Session, select

from app.models import DocumentoAdjunto
from app.schemas import DocumentoAdjuntoCreate, DocumentoAdjuntoUpdate
from app.core.config import EstadoValidacion
from app.utils import BaseRepository


class DocumentoAdjuntoRepository(BaseRepository[DocumentoAdjunto, DocumentoAdjuntoCreate, DocumentoAdjuntoUpdate]):
    def __init__(self):
        super().__init__(DocumentoAdjunto)

    def get_by_expediente_id(
        self,
        session: Session,
        expediente_id: int
    ) -> List[DocumentoAdjunto]:
        statement = (
            select(DocumentoAdjunto)
            .where(DocumentoAdjunto.id_expediente == expediente_id)
            .order_by(DocumentoAdjunto.fecha_subida)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_by_requisito_id(
        self,
        session: Session,
        requisito_id: int
    ) -> List[DocumentoAdjunto]:
        statement = select(DocumentoAdjunto).where(DocumentoAdjunto.id_requisito == requisito_id)
        results = session.exec(statement)
        return list(results.all())

    def get_by_estado(
        self,
        session: Session,
        estado: EstadoValidacion,
        expediente_id: int | None = None
    ) -> List[DocumentoAdjunto]:
        statement = select(DocumentoAdjunto).where(DocumentoAdjunto.estado_validacion == estado)
        if expediente_id:
            statement = statement.where(DocumentoAdjunto.id_expediente == expediente_id)
        results = session.exec(statement)
        return list(results.all())

    def update_estado(
        self,
        session: Session,
        id: int,
        nuevo_estado: EstadoValidacion,
        observaciones: str = ""
    ) -> Optional[DocumentoAdjunto]:
        db_obj = self.get_by_id(session=session, id=id)
        if db_obj is None:
            return None
        
        db_obj.estado_validacion = nuevo_estado
        if observaciones:
            db_obj.observaciones = observaciones
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj


documento_adjunto_repository = DocumentoAdjuntoRepository()
