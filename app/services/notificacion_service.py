from typing import List, Optional, Tuple
from datetime import datetime, timezone
from sqlmodel import Session

from app.models import Notificacion
from app.repositories import notificacion_repository
from app.schemas import (
    NotificacionCreate,
    NotificacionUpdate,
    NotificacionLeidaRequest
)


class NotificacionService:
    TIPOS_NOTIFICACION = {
        "EXPEDIENTE_ENVIADO": "Expediente enviado a revisión",
        "DOCUMENTO_APROBADO": "Documento aprobado",
        "DOCUMENTO_OBSERVADO": "Documento observado",
        "EXPEDIENTE_APROBADO": "Expediente aprobado",
        "EXPEDIENTE_RECHAZADO": "Expediente rechazado",
        "EXPEDIENTE_OBSERVADO": "Expediente observado",
        "CITA_PROGRAMADA": "Cita programada",
        "CITA_CANCELADA": "Cita cancelada",
        "INSPECCION_ASIGNADA": "Inspección asignada",
        "INSPECCION_RESULTADO": "Resultado de inspección disponible"
    }

    @staticmethod
    def crear_notificacion(
        session: Session,
        id_ciudadano: int,
        tipo: str,
        mensaje: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        notificacion = Notificacion(
            id_ciudadano=id_ciudadano,
            id_expediente=id_expediente,
            tipo=tipo,
            mensaje=mensaje,
            leido=False,
            fecha_envio=datetime.now(timezone.utc)
        )
        
        return notificacion_repository.create(session, notificacion)

    @staticmethod
    def notificar_expediente_enviado(
        session: Session,
        id_ciudadano: int,
        codigo_seguimiento: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        mensaje = f"Tu expediente {codigo_seguimiento} ha sido enviado a revisión."
        return NotificacionService.crear_notificacion(
            session,
            id_ciudadano,
            "EXPEDIENTE_ENVIADO",
            mensaje,
            id_expediente
        )

    @staticmethod
    def notificar_documento_observado(
        session: Session,
        id_ciudadano: int,
        nombre_documento: str,
        observaciones: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        mensaje = f"El documento '{nombre_documento}' tiene observaciones: {observaciones}"
        return NotificacionService.crear_notificacion(
            session,
            id_ciudadano,
            "DOCUMENTO_OBSERVADO",
            mensaje,
            id_expediente
        )

    @staticmethod
    def notificar_expediente_observado(
        session: Session,
        id_ciudadano: int,
        codigo_seguimiento: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        mensaje = f"Tu expediente {codigo_seguimiento} ha sido observado. Por favor revisa los documentos."
        return NotificacionService.crear_notificacion(
            session,
            id_ciudadano,
            "EXPEDIENTE_OBSERVADO",
            mensaje,
            id_expediente
        )

    @staticmethod
    def notificar_expediente_aprobado(
        session: Session,
        id_ciudadano: int,
        codigo_seguimiento: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        mensaje = f"¡Felicidades! Tu expediente {codigo_seguimiento} ha sido aprobado."
        return NotificacionService.crear_notificacion(
            session,
            id_ciudadano,
            "EXPEDIENTE_APROBADO",
            mensaje,
            id_expediente
        )

    @staticmethod
    def notificar_expediente_rechazado(
        session: Session,
        id_ciudadano: int,
        codigo_seguimiento: str,
        motivo: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        mensaje = f"Tu expediente {codigo_seguimiento} ha sido rechazado. Motivo: {motivo}"
        return NotificacionService.crear_notificacion(
            session,
            id_ciudadano,
            "EXPEDIENTE_RECHAZADO",
            mensaje,
            id_expediente
        )

    @staticmethod
    def notificar_cita_programada(
        session: Session,
        id_ciudadano: int,
        fecha: str,
        hora: str,
        id_expediente: Optional[int] = None
    ) -> Notificacion:
        mensaje = f"Tienes una cita programada para el {fecha} a las {hora}."
        return NotificacionService.crear_notificacion(
            session,
            id_ciudadano,
            "CITA_PROGRAMADA",
            mensaje,
            id_expediente
        )

    @staticmethod
    def obtener_notificaciones(
        session: Session,
        id_ciudadano: int,
        solo_no_leidas: bool = False
    ) -> Tuple[List[Notificacion], int, int]:
        from sqlmodel import select
        
        if solo_no_leidas:
            statement = select(Notificacion).where(
                Notificacion.id_ciudadano == id_ciudadano,
                Notificacion.leido == False
            ).order_by(Notificacion.fecha_envio.desc())
        else:
            statement = select(Notificacion).where(
                Notificacion.id_ciudadano == id_ciudadano
            ).order_by(Notificacion.fecha_envio.desc())
        
        notificaciones = list(session.exec(statement).all())
        
        statement_no_leidas = select(Notificacion).where(
            Notificacion.id_ciudadano == id_ciudadano,
            Notificacion.leido == False
        )
        no_leidas = len(list(session.exec(statement_no_leidas).all()))
        
        statement_total = select(Notificacion).where(
            Notificacion.id_ciudadano == id_ciudadano
        )
        total = len(list(session.exec(statement_total).all()))
        
        return notificaciones, total, no_leidas

    @staticmethod
    def marcar_como_leida(
        session: Session,
        notificacion_id: int,
        id_ciudadano: int
    ) -> Optional[Notificacion]:
        notificacion = notificacion_repository.get_by_id(session, notificacion_id)
        if not notificacion:
            return None
        
        if notificacion.id_ciudadano != id_ciudadano:
            raise ValueError("Esta notificación no pertenece al usuario")
        
        update_data = NotificacionUpdate(leido=True)
        return notificacion_repository.update(session, notificacion, update_data)

    @staticmethod
    def marcar_todas_como_leidas(
        session: Session,
        id_ciudadano: int
    ) -> int:
        from sqlmodel import select, update
        
        statement = update(Notificacion).where(
            Notificacion.id_ciudadano == id_ciudadano,
            Notificacion.leido == False
        ).values(leido=True)
        
        result = session.exec(statement)
        session.commit()
        
        return result.rowcount


notificacion_service = NotificacionService()
