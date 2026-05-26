from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_ciudadano_obj,
    get_current_funcionario_obj,
)
from app.schemas import (
    CitaAsignarRequest,
    CitaResponse,
    CitaDisponibilidadResponse,
)
from app.models import Ciudadano, Empleado, Cita, Expediente
from app.services import cita_service, tramite_service, notificacion_service

router = APIRouter(prefix="/api/citas", tags=["Citas"])


@router.get("/disponibilidad", response_model=CitaDisponibilidadResponse)
def obtener_horarios_disponibles(
    fecha: date = Query(..., description="Fecha para verificar disponibilidad"),
    _ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    horarios = cita_service.obtener_horarios_disponibles(session, fecha)
    
    return CitaDisponibilidadResponse(
        fecha=fecha,
        horarios_disponibles=horarios
    )


@router.post(
    "/programar",
    response_model=CitaResponse,
    status_code=status.HTTP_201_CREATED
)
def programar_cita(
    body: CitaAsignarRequest,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, body.id_expediente)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para programar citas para este expediente"
        )
    
    try:
        cita = cita_service.programar_cita(
            session=session,
            cita_data=body,
            id_funcionario=None
        )
        
        notificacion_service.notificar_cita_programada(
            session=session,
            id_ciudadano=ciudadano.id,
            fecha=str(body.fecha),
            hora=str(body.hora_inicio),
            id_expediente=body.id_expediente
        )
        
        return cita
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/mis-citas", response_model=List[CitaResponse])
def mis_citas(
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    from sqlmodel import select
    
    statement = select(Cita).join(
        Expediente, Cita.id_expediente == Expediente.id
    ).where(
        Expediente.id_ciudadano == ciudadano.id
    ).order_by(Cita.fecha.desc(), Cita.hora_inicio.desc())
    
    citas = session.exec(statement).all()
    return list(citas)


@router.get("/{id}", response_model=CitaResponse)
def obtener_cita(
    id: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    cita = cita_service.obtener_cita(session, id)
    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    expediente = tramite_service.obtener_expediente(session, cita.id_expediente)
    if expediente and expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver esta cita"
        )
    
    return cita


@router.delete("/{id}", status_code=status.HTTP_200_OK)
def cancelar_cita(
    id: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    cita = cita_service.obtener_cita(session, id)
    if not cita:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cita no encontrada"
        )
    
    expediente = tramite_service.obtener_expediente(session, cita.id_expediente)
    if expediente and expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para cancelar esta cita"
        )
    
    try:
        cita_service.cancelar_cita(session, id)
        return {"mensaje": "Cita cancelada exitosamente"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/funcionario/mis-citas", response_model=List[CitaResponse])
def citas_funcionario(
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    citas = cita_service.obtener_citas_funcionario(session, empleado.id)
    return citas
