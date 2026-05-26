from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_funcionario_obj,
    get_current_gerente_obj,
)
from app.core.config import NivelRiesgo
from app.schemas import (
    DocumentoValidacionRequest,
    DocumentoAdjuntoResponse,
    ExpedienteResponse,
    ExpedienteUpdate,
)
from app.models import Empleado, Expediente, DocumentoAdjunto
from app.services import evaluacion_service, notificacion_service, tramite_service

router = APIRouter(prefix="/api/evaluacion", tags=["Evaluación"])


@router.get("/pendientes", response_model=List[ExpedienteResponse])
def listar_pendientes(
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    expedientes = evaluacion_service.obtener_expedientes_pendientes(session)
    return expedientes


@router.get("/expedientes/{id}", response_model=ExpedienteResponse)
def detalle_expediente(
    id: int,
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    expediente = evaluacion_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    return expediente


@router.get("/expedientes/{id}/documentos", response_model=List[DocumentoAdjuntoResponse])
def listar_documentos_expediente(
    id: int,
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    documentos = evaluacion_service.obtener_documentos_expediente(session, id)
    return documentos


@router.post("/documentos/validar", response_model=DocumentoAdjuntoResponse)
def validar_documento(
    body: DocumentoValidacionRequest,
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    try:
        documento = evaluacion_service.validar_documento(
            session=session,
            validacion_data=body,
            id_funcionario=empleado.id
        )
        
        if documento:
            expediente = tramite_service.obtener_expediente(session, documento.id_expediente)
            
            if body.estado_validacion.value == "observado" and expediente:
                notificacion_service.notificar_documento_observado(
                    session=session,
                    id_ciudadano=expediente.id_ciudadano,
                    nombre_documento=documento.nombre_archivo,
                    observaciones=body.observaciones,
                    id_expediente=expediente.id
                )
        
        return documento
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/expedientes/{id}/finalizar", response_model=ExpedienteResponse)
def finalizar_revision(
    id: int,
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    expediente = evaluacion_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    try:
        expediente_actualizado = evaluacion_service.finalizar_revision(
            session=session,
            expediente_id=id,
            id_funcionario=empleado.id
        )
        
        if expediente_actualizado:
            if expediente_actualizado.estado.value == "observado":
                notificacion_service.notificar_expediente_observado(
                    session=session,
                    id_ciudadano=expediente_actualizado.id_ciudadano,
                    codigo_seguimiento=expediente_actualizado.codigo_seguimiento,
                    id_expediente=expediente_actualizado.id
                )
        
        return expediente_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/expedientes/{id}/riesgo", response_model=ExpedienteResponse)
def cambiar_nivel_riesgo(
    id: int,
    nivel_riesgo: NivelRiesgo,
    gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    try:
        expediente = evaluacion_service.clasificar_riesgo_manual(
            session=session,
            expediente_id=id,
            nuevo_riesgo=nivel_riesgo,
            id_funcionario=gerente.id
        )
        return expediente
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
