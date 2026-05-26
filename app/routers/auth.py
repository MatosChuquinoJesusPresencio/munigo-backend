from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_user_obj,
    get_current_user,
)
from app.core.config import RolUsuario
from app.schemas import (
    RegistroRequest,
    UsuarioLogin,
    Token,
    UsuarioResponse,
    CiudadanoResponse,
    UsuarioCreate,
    CiudadanoCreate,
)
from app.models import Usuario, Ciudadano
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post(
    "/registro",
    response_model=UsuarioResponse,
    status_code=status.HTTP_201_CREATED
)
def registro(
    body: RegistroRequest,
    session: Session = Depends(get_session)
):
    try:
        usuario_data = UsuarioCreate(
            correo_electronico=body.correo_electronico,
            contrasena=body.contrasena
        )
        ciudadano_data = CiudadanoCreate(
            tipo_documento=body.tipo_documento,
            numero_documento=body.numero_documento,
            nombres_razon_social=body.nombres_razon_social,
            telefono=body.telefono,
            direccion=body.direccion
        )
        
        usuario, ciudadano = auth_service.register_ciudadano(
            session=session,
            usuario_data=usuario_data,
            ciudadano_data=ciudadano_data
        )
        
        return usuario
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
def login(
    body: UsuarioLogin,
    session: Session = Depends(get_session)
):
    try:
        usuario = auth_service.authenticate(session, body)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )
        
        return auth_service.create_token(usuario)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=UsuarioResponse)
def me(
    usuario: Usuario = Depends(get_current_user_obj)
):
    return usuario


@router.get("/me/ciudadano", response_model=CiudadanoResponse)
def me_ciudadano(
    usuario: Usuario = Depends(get_current_user_obj),
    session: Session = Depends(get_session)
):
    ciudadano = auth_service.get_ciudadano_by_usuario(session, usuario.id)
    if not ciudadano:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil de ciudadano no encontrado"
        )
    return ciudadano
