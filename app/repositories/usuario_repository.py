from typing import Optional

from sqlmodel import Session, select

from app.models import Usuario
from app.schemas import UsuarioCreate, UsuarioUpdate
from app.utils import BaseRepository


class UsuarioRepository(BaseRepository[Usuario, UsuarioCreate, UsuarioUpdate]):
    def __init__(self):
        super().__init__(Usuario)

    def get_by_email(
        self,
        session: Session,
        email: str
    ) -> Optional[Usuario]:
        statement = select(Usuario).where(Usuario.correo_electronico == email)
        results = session.exec(statement)
        return results.first()

    def exists_by_email(
        self,
        session: Session,
        email: str
    ) -> bool:
        statement = select(Usuario).where(Usuario.correo_electronico == email)
        results = session.exec(statement)
        return results.first() is not None


usuario_repository = UsuarioRepository()
