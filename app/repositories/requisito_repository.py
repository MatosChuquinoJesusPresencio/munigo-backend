from typing import Optional, List

from sqlmodel import Session, select

from app.models import Requisito
from app.schemas import RequisitoCreate, RequisitoUpdate
from app.core.config import TipoTramite
from app.utils import BaseRepository


class RequisitoRepository(BaseRepository[Requisito, RequisitoCreate, RequisitoUpdate]):
    def __init__(self):
        super().__init__(Requisito)

    def get_by_tipo_tramite(
        self,
        session: Session,
        tipo_tramite: TipoTramite
    ) -> List[Requisito]:
        statement = (
            select(Requisito)
            .where((Requisito.aplica_a == tipo_tramite) | (Requisito.aplica_a == None))
            .order_by(Requisito.id)
        )
        results = session.exec(statement)
        return list(results.all())

    def get_obligatorios(
        self,
        session: Session,
        tipo_tramite: TipoTramite | None = None
    ) -> List[Requisito]:
        statement = select(Requisito).where(Requisito.es_obligatorio == True)
        if tipo_tramite:
            statement = statement.where((Requisito.aplica_a == tipo_tramite) | (Requisito.aplica_a == None))
        statement = statement.order_by(Requisito.id)
        results = session.exec(statement)
        return list(results.all())

    def get_by_nombre(
        self,
        session: Session,
        nombre: str
    ) -> Optional[Requisito]:
        statement = select(Requisito).where(Requisito.nombre == nombre)
        results = session.exec(statement)
        return results.first()


requisito_repository = RequisitoRepository()
