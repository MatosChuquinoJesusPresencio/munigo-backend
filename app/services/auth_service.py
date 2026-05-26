from typing import Optional, Tuple
from sqlmodel import Session

from app.core.config import RolUsuario
from app.core.security import (
    get_password_hash,
    verify_password,
    create_token_for_user
)
from app.models import Usuario, Ciudadano
from app.repositories import usuario_repository, ciudadano_repository
from app.schemas import (
    UsuarioCreate,
    UsuarioLogin,
    CiudadanoCreate,
    Token,
    UsuarioResponse,
    CiudadanoResponse
)


class AuthService:
    @staticmethod
    def register_ciudadano(
        session: Session,
        usuario_data: UsuarioCreate,
        ciudadano_data: CiudadanoCreate
    ) -> Tuple[Usuario, Ciudadano]:
        if usuario_repository.exists_by_email(session, usuario_data.correo_electronico):
            raise ValueError("El correo electrónico ya está registrado")
        
        hashed_password = get_password_hash(usuario_data.contrasena)
        
        usuario = Usuario(
            correo_electronico=usuario_data.correo_electronico,
            contrasena=hashed_password,
            rol=RolUsuario.CIUDADANO
        )
        usuario = usuario_repository.create(session, usuario)
        
        ciudadano = Ciudadano(
            id_usuario=usuario.id,
            tipo_documento=ciudadano_data.tipo_documento,
            numero_documento=ciudadano_data.numero_documento,
            nombres_razon_social=ciudadano_data.nombres_razon_social,
            telefono=ciudadano_data.telefono,
            direccion=ciudadano_data.direccion
        )
        ciudadano = ciudadano_repository.create(session, ciudadano)
        
        return usuario, ciudadano

    @staticmethod
    def authenticate(
        session: Session,
        login_data: UsuarioLogin
    ) -> Optional[Usuario]:
        usuario = usuario_repository.get_by_email(session, login_data.correo_electronico)
        
        if not usuario:
            return None
        
        if not verify_password(login_data.contrasena, usuario.contrasena):
            return None
        
        if not usuario.activo:
            raise ValueError("Usuario inactivo")
        
        return usuario

    @staticmethod
    def create_token(usuario: Usuario) -> Token:
        access_token = create_token_for_user(
            user_id=usuario.id,
            email=usuario.correo_electronico,
            role=usuario.rol
        )
        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_current_user(
        session: Session,
        user_id: int
    ) -> Optional[Usuario]:
        return usuario_repository.get_by_id(session, user_id)

    @staticmethod
    def get_ciudadano_by_usuario(
        session: Session,
        user_id: int
    ) -> Optional[Ciudadano]:
        from sqlmodel import select
        statement = select(Ciudadano).where(Ciudadano.id_usuario == user_id)
        results = session.exec(statement)
        return results.first()


auth_service = AuthService()
