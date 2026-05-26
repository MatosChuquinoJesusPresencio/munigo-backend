from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, Dict, Any
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_user_obj,
    get_current_ciudadano_obj,
)
from app.schemas import (
    NotificacionResponse,
    NotificacionListaResponse,
    NotificacionLeidaRequest,
)
from app.models import Usuario, Ciudadano
from app.services import notificacion_service

notificaciones_router = APIRouter(prefix="/api/notificaciones", tags=["Notificaciones"])


@notificaciones_router.get("", response_model=NotificacionListaResponse)
def listar_notificaciones(
    solo_no_leidas: bool = False,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    notificaciones, total, no_leidas = notificacion_service.obtener_notificaciones(
        session=session,
        id_ciudadano=ciudadano.id,
        solo_no_leidas=solo_no_leidas
    )
    
    return NotificacionListaResponse(
        total=total,
        no_leidas=no_leidas,
        notificaciones=notificaciones
    )


@notificaciones_router.get("/no-leidas", response_model=NotificacionListaResponse)
def listar_no_leidas(
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    notificaciones, total, no_leidas = notificacion_service.obtener_notificaciones(
        session=session,
        id_ciudadano=ciudadano.id,
        solo_no_leidas=True
    )
    
    return NotificacionListaResponse(
        total=total,
        no_leidas=no_leidas,
        notificaciones=notificaciones
    )


@notificaciones_router.put("/{id}/leida", status_code=status.HTTP_200_OK)
def marcar_como_leida(
    id: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    try:
        notificacion_service.marcar_como_leida(
            session=session,
            notificacion_id=id,
            id_ciudadano=ciudadano.id
        )
        return {"mensaje": "Notificación marcada como leída"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@notificaciones_router.post("/marcar-todas", status_code=status.HTTP_200_OK)
def marcar_todas_como_leidas(
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    cantidad = notificacion_service.marcar_todas_como_leidas(
        session=session,
        id_ciudadano=ciudadano.id
    )
    
    return {
        "mensaje": f"{cantidad} notificaciones marcadas como leídas",
        "cantidad": cantidad
    }
