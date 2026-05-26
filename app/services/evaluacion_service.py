from typing import List, Optional
from sqlmodel import Session

from app.core.config import (
    EstadoTramite,
    NivelRiesgo,
    EstadoValidacion,
    RolUsuario
)
from app.models import Expediente, DocumentoAdjunto
from app.repositories import (
    expediente_repository,
    documento_adjunto_repository,
    empleado_repository
)
from app.schemas import (
    ExpedienteUpdate,
    DocumentoAdjuntoUpdate,
    DocumentoValidacionRequest,
    ExpedienteRiesgoResponse
)


class EvaluacionService:
    @staticmethod
    def obtener_expedientes_pendientes(
        session: Session
    ) -> List[Expediente]:
        from sqlmodel import select
        statement = select(Expediente).where(
            Expediente.estado == EstadoTramite.PENDIENTE_REVISION
        ).order_by(Expediente.fecha_ingreso)
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def obtener_expediente(
        session: Session,
        expediente_id: int
    ) -> Optional[Expediente]:
        return expediente_repository.get_by_id(session, expediente_id)

    @staticmethod
    def obtener_documentos_expediente(
        session: Session,
        id_expediente: int
    ) -> List[DocumentoAdjunto]:
        from sqlmodel import select
        statement = select(DocumentoAdjunto).where(DocumentoAdjunto.id_expediente == id_expediente)
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def validar_documento(
        session: Session,
        validacion_data: DocumentoValidacionRequest,
        id_funcionario: int
    ) -> Optional[DocumentoAdjunto]:
        documento = documento_adjunto_repository.get_by_id(
            session,
            validacion_data.id_documento
        )
        if not documento:
            return None
        
        update_data = DocumentoAdjuntoUpdate(
            estado_validacion=validacion_data.estado_validacion,
            observaciones=validacion_data.observaciones
        )
        
        return documento_adjunto_repository.update(session, documento, update_data)

    @staticmethod
    def _todos_documentos_aprobados(
        session: Session,
        id_expediente: int
    ) -> bool:
        from sqlmodel import select
        statement = select(DocumentoAdjunto).where(
            DocumentoAdjunto.id_expediente == id_expediente
        )
        resultados = session.exec(statement).all()
        
        if not resultados:
            return False
        
        for doc in resultados:
            if doc.estado_validacion != EstadoValidacion.APROBADO:
                return False
        
        return True

    @staticmethod
    def _hay_documentos_observados(
        session: Session,
        id_expediente: int
    ) -> bool:
        from sqlmodel import select
        statement = select(DocumentoAdjunto).where(
            DocumentoAdjunto.id_expediente == id_expediente,
            DocumentoAdjunto.estado_validacion == EstadoValidacion.OBSERVADO
        )
        resultado = session.exec(statement).first()
        return resultado is not None

    @staticmethod
    def finalizar_revision(
        session: Session,
        expediente_id: int,
        id_funcionario: int
    ) -> Optional[Expediente]:
        expediente = expediente_repository.get_by_id(session, expediente_id)
        if not expediente:
            return None
        
        if expediente.estado != EstadoTramite.PENDIENTE_REVISION:
            raise ValueError("El expediente no está en estado PENDIENTE_REVISION")
        
        if EvaluacionService._hay_documentos_observados(session, expediente_id):
            update_data = ExpedienteUpdate(estado=EstadoTramite.OBSERVADO)
            return expediente_repository.update(session, expediente, update_data)
        
        if not EvaluacionService._todos_documentos_aprobados(session, expediente_id):
            raise ValueError("No se puede finalizar la revisión hasta que todos los documentos estén validados")
        
        if expediente.nivel_riesgo == NivelRiesgo.ALTO:
            update_data = ExpedienteUpdate(estado=EstadoTramite.PENDIENTE_INSPECCION)
        else:
            update_data = ExpedienteUpdate(estado=EstadoTramite.DOCUMENTOS_APROBADOS)
        
        return expediente_repository.update(session, expediente, update_data)

    @staticmethod
    def puede_revisar_expediente(
        session: Session,
        expediente_id: int,
        id_funcionario: int
    ) -> bool:
        empleado = empleado_repository.get_by_id(session, id_funcionario)
        if not empleado:
            return False
        
        expediente = expediente_repository.get_by_id(session, expediente_id)
        if not expediente:
            return False
        
        if empleado.cargo == "gerente":
            return True
        
        if expediente.nivel_riesgo == NivelRiesgo.ALTO and empleado.cargo != "gerente":
            return False
        
        return True

    @staticmethod
    def clasificar_riesgo_manual(
        session: Session,
        expediente_id: int,
        nuevo_riesgo: NivelRiesgo,
        id_funcionario: int
    ) -> Optional[Expediente]:
        empleado = empleado_repository.get_by_id(session, id_funcionario)
        if not empleado or empleado.cargo != "gerente":
            raise ValueError("Solo los gerentes pueden clasificar riesgo manualmente")
        
        expediente = expediente_repository.get_by_id(session, expediente_id)
        if not expediente:
            return None
        
        update_data = ExpedienteUpdate(nivel_riesgo=nuevo_riesgo)
        return expediente_repository.update(session, expediente, update_data)


evaluacion_service = EvaluacionService()
