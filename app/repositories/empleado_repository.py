from typing import Optional, List

from sqlmodel import Session, select

from app.models import Empleado
from app.schemas import EmpleadoCreate, EmpleadoUpdate
from app.core.config import RolUsuario
from app.utils import BaseRepository


class EmpleadoRepository(BaseRepository[Empleado, EmpleadoCreate, EmpleadoUpdate]):
    def __init__(self):
        super().__init__(Empleado)

    def get_by_usuario_id(
        self,
        session: Session,
        usuario_id: int
    ) -> Optional[Empleado]:
        statement = select(Empleado).where(Empleado.id_usuario == usuario_id)
        results = session.exec(statement)
        return results.first()

    def get_by_area(
        self,
        session: Session,
        area: str
    ) -> List[Empleado]:
        statement = select(Empleado).where(Empleado.area == area)
        results = session.exec(statement)
        return list(results.all())

    def get_inspectores(
        self,
        session: Session
    ) -> List[Empleado]:
        from app.models import Usuario
        statement = (
            select(Empleado)
            .join(Usuario, Usuario.id == Empleado.id_usuario)
            .where(Usuario.rol == RolUsuario.INSPECTOR)
        )
        results = session.exec(statement)
        return list(results.all())


empleado_repository = EmpleadoRepository()
