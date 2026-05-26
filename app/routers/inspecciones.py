from datetime import date, datetime
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    status,
)
from typing import List, Optional
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_inspector_obj,
    get_current_funcionario_obj,
    get_current_ciudadano_obj,
)
from app.core.config import settings
from app.core.storage import storage
from app.schemas import (
    InspeccionAsignarRequest,
    InspeccionResultadoRequest,
    InspeccionResponse,
    HojaRutaResponse,
    HojaRutaItem,
)
from app.models import Empleado, Ciudadano, Inspeccion, Expediente
from app.services import inspeccion_service, tramite_service, notificacion_service

router = APIRouter(prefix="/api/inspecciones", tags=["Inspección y Control"])


@router.post(
    "/asignar",
    response_model=InspeccionResponse,
    status_code=status.HTTP_201_CREATED
)
def asignar_inspeccion(
    body: InspeccionAsignarRequest,
    empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, body.id_expediente)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    try:
        inspeccion = inspeccion_service.asignar_inspeccion(session, body)
        return inspeccion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/hoja-ruta", response_model=HojaRutaResponse)
def obtener_hoja_ruta(
    fecha: Optional[date] = None,
    inspector: Empleado = Depends(get_current_inspector_obj),
    session: Session = Depends(get_session)
):
    if fecha is None:
        fecha = datetime.now().date()
    
    fecha_datetime = datetime.combine(fecha, datetime.min.time())
    
    items_raw = inspeccion_service.obtener_hoja_ruta(
        session=session,
        id_inspector=inspector.id,
        fecha=fecha_datetime
    )
    
    items = []
    for item in items_raw:
        items.append(HojaRutaItem(
            id_inspeccion=item["id_inspeccion"],
            id_expediente=item["id_expediente"],
            direccion_local=item["direccion_local"],
            zona=item["zona"],
            fecha_programada=item["fecha_programada"]
        ))
    
    return HojaRutaResponse(
        inspector_id=inspector.id,
        inspector_nombre=f"{inspector.nombres} {inspector.apellidos}",
        fecha=fecha_datetime,
        inspecciones=items
    )


@router.get("/mis-inspecciones", response_model=List[InspeccionResponse])
def mis_inspecciones(
    inspector: Empleado = Depends(get_current_inspector_obj),
    session: Session = Depends(get_session)
):
    inspecciones = inspeccion_service.obtener_inspecciones_inspector(session, inspector.id)
    return inspecciones


@router.get("/{id}", response_model=InspeccionResponse)
def obtener_inspeccion(
    id: int,
    inspector: Empleado = Depends(get_current_inspector_obj),
    session: Session = Depends(get_session)
):
    inspeccion = inspeccion_service.obtener_inspeccion(session, id)
    if not inspeccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspección no encontrada"
        )
    
    if inspeccion.id_inspector != inspector.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver esta inspección"
        )
    
    return inspeccion


@router.post("/{id}/resultado", response_model=InspeccionResponse)
async def registrar_resultado(
    id: int,
    resultado: str = Form(...),
    comentarios: str = Form(""),
    foto: Optional[UploadFile] = File(None),
    inspector: Empleado = Depends(get_current_inspector_obj),
    session: Session = Depends(get_session)
):
    inspeccion = inspeccion_service.obtener_inspeccion(session, id)
    if not inspeccion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspección no encontrada"
        )
    
    if inspeccion.id_inspector != inspector.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para registrar el resultado de esta inspección"
        )
    
    foto_ruta = ""
    if foto and foto.filename:
        content = await foto.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La foto excede el tamaño máximo de {settings.MAX_UPLOAD_SIZE / 1024 / 1024} MB"
            )
        
        foto_ruta = storage.save(content, foto.filename, subdir="inspecciones")
    
    from app.core.config import ResultadoInspeccion
    try:
        resultado_enum = ResultadoInspeccion(resultado.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resultado inválido. Valores permitidos: {[r.value for r in ResultadoInspeccion]}"
        )
    
    request_data = InspeccionResultadoRequest(
        resultado=resultado_enum,
        comentarios=comentarios,
        foto_ruta=foto_ruta
    )
    
    try:
        inspeccion_actualizada = inspeccion_service.registrar_resultado(
            session=session,
            inspeccion_id=id,
            resultado_data=request_data,
            id_inspector=inspector.id
        )
        
        if inspeccion_actualizada:
            expediente = tramite_service.obtener_expediente(session, inspeccion_actualizada.id_expediente)
            if expediente:
                if resultado_enum.value == "aprobado":
                    notificacion_service.notificar_expediente_aprobado(
                        session=session,
                        id_ciudadano=expediente.id_ciudadano,
                        codigo_seguimiento=expediente.codigo_seguimiento,
                        id_expediente=expediente.id
                    )
                elif resultado_enum.value == "no_aprobado":
                    notificacion_service.notificar_expediente_rechazado(
                        session=session,
                        id_ciudadano=expediente.id_ciudadano,
                        codigo_seguimiento=expediente.codigo_seguimiento,
                        motivo=comentarios,
                        id_expediente=expediente.id
                    )
        
        return inspeccion_actualizada
    except ValueError as e:
        if foto_ruta:
            storage.delete(foto_ruta)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/expediente/{id_expediente}", response_model=List[InspeccionResponse])
def inspecciones_expediente(
    id_expediente: int,
    ciudadano: Ciudadano = Depends(get_current_ciudadano_obj),
    session: Session = Depends(get_session)
):
    expediente = tramite_service.obtener_expediente(session, id_expediente)
    if not expediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expediente no encontrado"
        )
    
    if expediente.id_ciudadano != ciudadano.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos para ver estas inspecciones"
        )
    
    inspecciones = inspeccion_service.obtener_inspecciones_expediente(session, id_expediente)
    return inspecciones
