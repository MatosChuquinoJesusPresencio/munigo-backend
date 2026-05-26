from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
)
from typing import Optional, List
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_ciudadano_obj,
    get_current_funcionario_obj,
)
from app.core.config import settings
from app.core.storage import storage
from app.schemas import (
    ExpedienteCreate,
    ExpedienteUpdate,
    ExpedienteResponse,
    DocumentoAdjuntoResponse,
    DocumentoSubidoResponse,
    ExpedienteRiesgoRequest,
    ExpedienteRiesgoResponse,
)
from app.models import Ciudadano, Empleado, Expediente, DocumentoAdjunto
from app.services import tramite_service, notificacion_service

tramites_router = APIRouter(prefix="/api/tramites", tags=["Gestión de Trámites"])


@tramites_router.get("/mis-tramites", response_model=List[ExpedienteResponse])
def mis_tramites(
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expedientes = tramite_service.obtener_expedientes_ciudadano(session, ciudadano.id)
    return expedientes


@tramites_router.post(
    "",
    response_model=ExpedienteResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_expediente(
    body: ExpedienteCreate,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    try:
        expediente = tramite_service.crear_expediente(
            session=session,
            id_ciudadano=ciudadano.id,
            expediente_data=body
        )
        return expediente
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@tramites_router.get("/{id}", response_model=ExpedienteResponse)
def ver_expediente(
    id: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver este expediente"
        )
    
    return expediente


@tramites_router.put("/{id}", response_model=ExpedienteResponse)
def actualizar_expediente(
    id: int,
    body: ExpedienteUpdate,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para editar este expediente"
        )
    
    try:
        expediente_actualizado = tramite_service.actualizar_expediente(
            session=session,
            expediente_id=id,
            update_data=body
        )
        return expediente_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@tramites_router.post("/{id}/enviar", response_model=ExpedienteResponse)
def enviar_expediente(
    id: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para enviar este expediente"
        )
    
    try:
        expediente_actualizado = tramite_service.enviar_expediente(session, id)
        
        notificacion_service.notificar_expediente_enviado(
            session=session,
            id_ciudadano=ciudadano.id,
            codigo_seguimiento=expediente_actualizado.codigo_seguimiento,
            id_expediente=expediente_actualizado.id
        )
        
        return expediente_actualizado
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@tramites_router.get("/{id}/documentos", response_model=List[DocumentoAdjuntoResponse])
def listar_documentos(
    id: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver estos documentos"
        )
    
    documentos = tramite_service.obtener_documentos_expediente(session, id)
    return documentos


@tramites_router.post(
    "/{id}/documentos",
    response_model=DocumentoSubidoResponse,
    status_code=status.HTTP_201_CREATED
)
async def subir_documento(
    id: int,
    id_requisito: Optional[int] = Form(None),
    file: UploadFile = File(...),
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, id)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para subir documentos a este expediente"
        )
    
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El archivo excede el tamaño máximo de {settings.MAX_UPLOAD_SIZE / 1024 / 1024} MB"
        )
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo no tiene nombre"
        )
    
    try:
        relative_path = storage.save(content, file.filename, subdir="documentos")
        
        documento = tramite_service.subir_documento(
            session=session,
            id_expediente=id,
            id_requisito=id_requisito,
            nombre_archivo=file.filename,
            ruta_archivo=relative_path
        )
        
        return DocumentoSubidoResponse(
            id=documento.id,
            nombre_archivo=documento.nombre_archivo,
            estado_validacion=documento.estado_validacion,
            mensaje="Documento subido exitosamente"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@tramites_router.post("/clasificar-riesgo", response_model=ExpedienteRiesgoResponse)
def clasificar_riesgo_simulado(
    body: ExpedienteRiesgoRequest
):
    nivel_riesgo = tramite_service.clasificar_riesgo(
        giro=body.giro,
        tamano=body.tamano_local
    )
    
    requiere_inspeccion = tramite_service.requiere_inspeccion(nivel_riesgo)
    
    motivos = {
        "bajo": "Riesgo bajo según giro y tamaño del local",
        "medio": "Riesgo medio según giro y tamaño del local",
        "alto": "Riesgo alto - requiere inspección obligatoria según giro o tamaño"
    }
    
    return ExpedienteRiesgoResponse(
        nivel_riesgo=nivel_riesgo,
        requiere_inspeccion=requiere_inspeccion,
        motivo=motivos.get(nivel_riesgo.value, "Clasificación estándar")
    )


@tramites_router.get("/pendientes/revision", response_model=List[ExpedienteResponse])
def listar_pendientes_revision(
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    from app.services import evaluacion_service
    expedientes = evaluacion_service.obtener_expedientes_pendientes(session)
    return expedientes
