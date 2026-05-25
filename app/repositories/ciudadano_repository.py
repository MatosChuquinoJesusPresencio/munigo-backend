from typing import Optional, List

from sqlmodel import Session, select

from app.models import Ciudadano
from app.schemas import CiudadanoCreate, CiudadanoUpdate
from app.utils import BaseRepository


class CiudadanoRepository(BaseRepository[Ciudadano, CiudadanoCreate, CiudadanoUpdate]):
    def __init__(self):
        super().__init__(Ciudadano)

    def get_by_usuario_id(
        self,
        session: Session,
        usuario_id: int
    ) -> Optional[Ciudadano]:
        statement = select(Ciudadano).where(Ciudadano.id_usuario == usuario_id)
        results = session.exec(statement)
        return results.first()

    def get_by_numero_documento(
        self,
        session: Session,
        numero_documento: str
    ) -> Optional[Ciudadano]:
        statement = select(Ciudadano).where(Ciudadano.numero_documento == numero_documento)
        results = session.exec(statement)
        return results.first()


ciudadano_repository = CiudadanoRepository()
