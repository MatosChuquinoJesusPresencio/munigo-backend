from app.repositories.usuario_repository import UsuarioRepository, usuario_repository
from app.repositories.ciudadano_repository import CiudadanoRepository, ciudadano_repository
from app.repositories.empleado_repository import EmpleadoRepository, empleado_repository
from app.repositories.expediente_repository import ExpedienteRepository, expediente_repository
from app.repositories.documento_adjunto_repository import DocumentoAdjuntoRepository, documento_adjunto_repository
from app.repositories.cita_repository import CitaRepository, cita_repository
from app.repositories.inspeccion_repository import InspeccionRepository, inspeccion_repository
from app.repositories.notificacion_repository import NotificacionRepository, notificacion_repository
from app.repositories.requisito_repository import RequisitoRepository, requisito_repository
from app.repositories.tramite_requisito_repository import TramiteRequisitoRepository, tramite_requisito_repository

__all__ = [
    "UsuarioRepository",
    "usuario_repository",
    "CiudadanoRepository",
    "ciudadano_repository",
    "EmpleadoRepository",
    "empleado_repository",
    "ExpedienteRepository",
    "expediente_repository",
    "DocumentoAdjuntoRepository",
    "documento_adjunto_repository",
    "CitaRepository",
    "cita_repository",
    "InspeccionRepository",
    "inspeccion_repository",
    "NotificacionRepository",
    "notificacion_repository",
    "RequisitoRepository",
    "requisito_repository",
    "TramiteRequisitoRepository",
    "tramite_requisito_repository",
]
