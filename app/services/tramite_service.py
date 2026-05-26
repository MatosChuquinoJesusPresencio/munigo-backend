import random
import string
from typing import List, Optional
from datetime import datetime, timezone
from sqlmodel import Session

from app.core.config import (
    EstadoTramite,
    NivelRiesgo,
    TipoTramite,
    EstadoValidacion
)
from app.models import Expediente, DocumentoAdjunto
from app.repositories import (
    expediente_repository,
    documento_adjunto_repository,
    tramite_requisito_repository
)
from app.schemas import (
    ExpedienteCreate,
    ExpedienteUpdate,
    DocumentoAdjuntoCreate,
    ExpedienteResponse,
    DocumentoSubidoResponse
)


class TramiteService:
    GIROS_ALTO_RIESGO = [
        "discoteca", "club nocturno", "bar", "pub", "cantina",
        "gasolinera", "estacion de servicio", "estación de servicio",
        "almacen peligroso", "almacén peligroso",
        "bodega quimicos", "bodega químicos",
        "hospital", "clinica", "clínica", "laboratorio"
    ]

    GIROS_MEDIO_RIESGO = [
        "restaurante", "cafeteria", "cafetería", "hotel",
        "centro comercial", "tienda departamental",
        "gimnasio", "spa"
    ]

    GIROS_BAJO_RIESGO = [
        "oficina", "consultorio", "estudio",
        "tienda pequena", "tienda pequeña", "panaderia", "panadería",
        "papeleria", "papelería", "bodega"
    ]

    @staticmethod
    def _normalizar_texto(texto: str) -> str:
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N'
        }
        for k, v in reemplazos.items():
            texto = texto.replace(k, v)
        return texto.lower()

    @staticmethod
    def _generar_codigo_seguimiento() -> str:
        prefijo = "EXP-"
        fecha = datetime.now(timezone.utc).strftime("%Y%m")
        aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefijo}{fecha}-{aleatorio}"

    def clasificar_riesgo(
        self,
        giro: str,
        tamano: int
    ) -> NivelRiesgo:
        giro_normalizado = self._normalizar_texto(giro)
        
        for palabra in self.GIROS_ALTO_RIESGO:
            palabra_norm = self._normalizar_texto(palabra)
            if palabra_norm in giro_normalizado:
                return NivelRiesgo.ALTO
        
        for palabra in self.GIROS_MEDIO_RIESGO:
            palabra_norm = self._normalizar_texto(palabra)
            if palabra_norm in giro_normalizado:
                if "restaurante" in palabra_norm and tamano > 200:
                    return NivelRiesgo.ALTO
                if "restaurante" in palabra_norm:
                    return NivelRiesgo.MEDIO
                if ("cafe" in palabra_norm or "panaderia" in palabra_norm) and tamano <= 100:
                    return NivelRiesgo.BAJO
                return NivelRiesgo.MEDIO
        
        for palabra in self.GIROS_BAJO_RIESGO:
            palabra_norm = self._normalizar_texto(palabra)
            if palabra_norm in giro_normalizado:
                return NivelRiesgo.BAJO
        
        if tamano > 500:
            return NivelRiesgo.ALTO
        elif tamano > 200:
            return NivelRiesgo.MEDIO
        else:
            return NivelRiesgo.BAJO

    @staticmethod
    def requiere_inspeccion(nivel_riesgo: NivelRiesgo) -> bool:
        return nivel_riesgo == NivelRiesgo.ALTO

    def crear_expediente(
        self,
        session: Session,
        id_ciudadano: int,
        expediente_data: ExpedienteCreate
    ) -> Expediente:
        nivel_riesgo = self.clasificar_riesgo(
            expediente_data.giro,
            expediente_data.tamano_local
        )
        
        expediente = Expediente(
            id_ciudadano=id_ciudadano,
            tipo_tramite=expediente_data.tipo_tramite,
            nivel_riesgo=nivel_riesgo,
            codigo_seguimiento=self._generar_codigo_seguimiento(),
            giro=expediente_data.giro,
            tamano_local=expediente_data.tamano_local,
            direccion_local=expediente_data.direccion_local,
            zona=expediente_data.zona,
            estado=EstadoTramite.BORRADOR
        )
        
        return expediente_repository.create(session, expediente)

    @staticmethod
    def obtener_expediente(
        session: Session,
        expediente_id: int
    ) -> Optional[Expediente]:
        return expediente_repository.get_by_id(session, expediente_id)

    @staticmethod
    def obtener_expedientes_ciudadano(
        session: Session,
        id_ciudadano: int
    ) -> List[Expediente]:
        from sqlmodel import select
        statement = select(Expediente).where(Expediente.id_ciudadano == id_ciudadano)
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def actualizar_expediente(
        session: Session,
        expediente_id: int,
        update_data: ExpedienteUpdate
    ) -> Optional[Expediente]:
        expediente = expediente_repository.get_by_id(session, expediente_id)
        if not expediente:
            return None
        
        if expediente.estado != EstadoTramite.BORRADOR:
            raise ValueError("Solo se pueden editar expedientes en estado BORRADOR")
        
        return expediente_repository.update(session, expediente, update_data)

    @staticmethod
    def subir_documento(
        session: Session,
        id_expediente: int,
        id_requisito: Optional[int],
        nombre_archivo: str,
        ruta_archivo: str
    ) -> DocumentoAdjunto:
        expediente = expediente_repository.get_by_id(session, id_expediente)
        if not expediente:
            raise ValueError("Expediente no encontrado")
        
        documento = DocumentoAdjunto(
            id_expediente=id_expediente,
            id_requisito=id_requisito,
            nombre_archivo=nombre_archivo,
            ruta_archivo=ruta_archivo,
            estado_validacion=EstadoValidacion.PENDIENTE
        )
        
        return documento_adjunto_repository.create(session, documento)

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
    def enviar_expediente(
        session: Session,
        expediente_id: int
    ) -> Optional[Expediente]:
        expediente = expediente_repository.get_by_id(session, expediente_id)
        if not expediente:
            return None
        
        if expediente.estado != EstadoTramite.BORRADOR:
            raise ValueError("Solo se pueden enviar expedientes en estado BORRADOR")
        
        documentos = TramiteService.obtener_documentos_expediente(session, expediente_id)
        if not documentos:
            raise ValueError("Debe subir al menos un documento antes de enviar")
        
        update_data = ExpedienteUpdate(estado=EstadoTramite.PENDIENTE_REVISION)
        return expediente_repository.update(session, expediente, update_data)


tramite_service = TramiteService()
