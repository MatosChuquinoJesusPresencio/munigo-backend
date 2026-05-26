from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Session

from app.core.config import EstadoTramite, ResultadoInspeccion
from app.models import Expediente, Inspeccion
from app.repositories import (
    expediente_repository,
    inspeccion_repository,
    empleado_repository
)
from app.schemas import (
    InspeccionCreate,
    InspeccionUpdate,
    InspeccionAsignarRequest,
    InspeccionResultadoRequest
)


class InspeccionService:
    @staticmethod
    def asignar_inspeccion(
        session: Session,
        asignacion_data: InspeccionAsignarRequest
    ) -> Inspeccion:
        expediente = expediente_repository.get_by_id(session, asignacion_data.id_expediente)
        if not expediente:
            raise ValueError("Expediente no encontrado")
        
        if expediente.estado != EstadoTramite.PENDIENTE_INSPECCION:
            raise ValueError("Solo se pueden asignar inspecciones a expedientes en PENDIENTE_INSPECCION")
        
        inspector = empleado_repository.get_by_id(session, asignacion_data.id_inspector)
        if not inspector:
            raise ValueError("Inspector no encontrado")
        
        inspeccion = Inspeccion(
            id_expediente=asignacion_data.id_expediente,
            id_inspector=asignacion_data.id_inspector,
            fecha_programada=asignacion_data.fecha_programada,
            resultado=ResultadoInspeccion.PENDIENTE,
            comentarios="",
            foto_ruta=""
        )
        
        return inspeccion_repository.create(session, inspeccion)

    @staticmethod
    def obtener_inspeccion(
        session: Session,
        inspeccion_id: int
    ) -> Optional[Inspeccion]:
        return inspeccion_repository.get_by_id(session, inspeccion_id)

    @staticmethod
    def obtener_inspecciones_expediente(
        session: Session,
        id_expediente: int
    ) -> List[Inspeccion]:
        from sqlmodel import select
        statement = select(Inspeccion).where(
            Inspeccion.id_expediente == id_expediente
        ).order_by(Inspeccion.fecha_creacion.desc())
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def obtener_inspecciones_inspector(
        session: Session,
        id_inspector: int
    ) -> List[Inspeccion]:
        from sqlmodel import select
        statement = select(Inspeccion).where(
            Inspeccion.id_inspector == id_inspector
        ).order_by(Inspeccion.fecha_programada)
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def obtener_hoja_ruta(
        session: Session,
        id_inspector: int,
        fecha: datetime
    ) -> List[dict]:
        fecha_inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        from sqlmodel import select
        statement = select(Inspeccion, Expediente).join(
            Expediente, Inspeccion.id_expediente == Expediente.id
        ).where(
            Inspeccion.id_inspector == id_inspector,
            Inspeccion.fecha_programada >= fecha_inicio,
            Inspeccion.fecha_programada <= fecha_fin,
            Inspeccion.resultado == ResultadoInspeccion.PENDIENTE
        ).order_by(Inspeccion.fecha_programada)
        
        results = session.exec(statement).all()
        
        hoja_ruta = []
        for inspeccion, expediente in results:
            hoja_ruta.append({
                "id_inspeccion": inspeccion.id,
                "id_expediente": expediente.id,
                "direccion_local": expediente.direccion_local,
                "zona": expediente.zona,
                "fecha_programada": inspeccion.fecha_programada
            })
        
        return hoja_ruta

    @staticmethod
    def registrar_resultado(
        session: Session,
        inspeccion_id: int,
        resultado_data: InspeccionResultadoRequest,
        id_inspector: int
    ) -> Optional[Inspeccion]:
        inspeccion = inspeccion_repository.get_by_id(session, inspeccion_id)
        if not inspeccion:
            return None
        
        if inspeccion.id_inspector != id_inspector:
            raise ValueError("Solo el inspector asignado puede registrar el resultado")
        
        if inspeccion.resultado != ResultadoInspeccion.PENDIENTE:
            raise ValueError("Esta inspección ya tiene un resultado registrado")
        
        update_data = InspeccionUpdate(
            fecha_ejecucion=datetime.now(timezone.utc),
            resultado=resultado_data.resultado,
            comentarios=resultado_data.comentarios,
            foto_ruta=resultado_data.foto_ruta
        )
        
        inspeccion_actualizada = inspeccion_repository.update(session, inspeccion, update_data)
        
        expediente = expediente_repository.get_by_id(session, inspeccion.id_expediente)
        if expediente:
            from app.schemas import ExpedienteUpdate
            
            if resultado_data.resultado == ResultadoInspeccion.APROBADO:
                expediente_update = ExpedienteUpdate(estado=EstadoTramite.APROBADO)
            else:
                expediente_update = ExpedienteUpdate(estado=EstadoTramite.RECHAZADO)
            
            expediente_repository.update(session, expediente, expediente_update)
        
        return inspeccion_actualizada


inspeccion_service = InspeccionService()
