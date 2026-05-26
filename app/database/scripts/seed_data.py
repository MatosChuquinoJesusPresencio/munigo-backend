from datetime import datetime, timezone
from typing import List, Dict, Tuple

from sqlmodel import Session, select

from app.database.connection import get_session, engine
from app.core.config import TipoTramite, RolUsuario
from app.core.security import get_password_hash
from app.models import Requisito, Usuario, Empleado
from app.repositories import requisito_repository, usuario_repository, empleado_repository


REQUISITOS_LICENCIA_FUNCIONAMIENTO: List[Dict] = [
    {
        "nombre": "DNI del Representante Legal",
        "descripcion": "Documento Nacional de Identidad del representante legal del establecimiento",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "RUC (Persona Jurídica)",
        "descripcion": "Registro Único de Contribuyente (si aplica para persona jurídica)",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": False,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "Declaración Jurada de No Infraestructura",
        "descripcion": "Declaración jurada que acredita que el local no requiere ITSE",
        "tipo_archivo_permitido": "pdf",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "Croquis de Ubicación",
        "descripcion": "Plano o croquis que indica la ubicación exacta del establecimiento",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "Plano de Distribución Interior",
        "descripcion": "Plano arquitectónico de la distribución interior del local",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "Certificado de Propiedad o Contrato de Alquiler",
        "descripcion": "Documento que acredita la propiedad o posesión del local",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "ITSE (si aplica)",
        "descripcion": "Inspección Técnica de Seguridad Estructural (si el local lo requiere)",
        "tipo_archivo_permitido": "pdf",
        "es_obligatorio": False,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
    {
        "nombre": "Pago de Derechos Municipales",
        "descripcion": "Comprobante de pago de los derechos municipales correspondientes",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.LICENCIA_FUNCIONAMIENTO,
    },
]


REQUISITOS_ITSE: List[Dict] = [
    {
        "nombre": "DNI del Propietario",
        "descripcion": "Documento Nacional de Identidad del propietario del inmueble",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.ITSE,
    },
    {
        "nombre": "Plano Arquitectónico",
        "descripcion": "Planos arquitectónicos aprobados del inmueble",
        "tipo_archivo_permitido": "pdf",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.ITSE,
    },
    {
        "nombre": "Plano Estructural",
        "descripcion": "Planos estructurales con cálculos de ingeniería",
        "tipo_archivo_permitido": "pdf",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.ITSE,
    },
    {
        "nombre": "Certificado de Suelos",
        "descripcion": "Estudio de mecánica de suelos del terreno",
        "tipo_archivo_permitido": "pdf",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.ITSE,
    },
    {
        "nombre": "Memoria Descriptiva",
        "descripcion": "Memoria descriptiva y de cálculo estructural",
        "tipo_archivo_permitido": "pdf",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.ITSE,
    },
    {
        "nombre": "Pago de Derechos ITSE",
        "descripcion": "Comprobante de pago de los derechos por Inspección Técnica",
        "tipo_archivo_permitido": "pdf,jpg,jpeg,png",
        "es_obligatorio": True,
        "aplica_a": TipoTramite.ITSE,
    },
]


ADMIN_CONFIG: Dict = {
    "correo_electronico": "admin@munigo.com",
    "contrasena": "admin123",
    "nombres": "Administrador",
    "apellidos": "Sistema",
    "cargo": "gerente",
    "area": "Gerencia General",
}


def seed_requisitos(session: Session) -> Tuple[int, int, int]:
    count_licencia = 0
    count_itse = 0
    
    for req_data in REQUISITOS_LICENCIA_FUNCIONAMIENTO:
        statement = select(Requisito).where(
            Requisito.nombre == req_data["nombre"],
            Requisito.aplica_a == req_data["aplica_a"]
        )
        existing = session.exec(statement).first()
        
        if not existing:
            requisito = Requisito(
                nombre=req_data["nombre"],
                descripcion=req_data["descripcion"],
                tipo_archivo_permitido=req_data["tipo_archivo_permitido"],
                es_obligatorio=req_data["es_obligatorio"],
                aplica_a=req_data["aplica_a"],
            )
            session.add(requisito)
            count_licencia += 1
    
    for req_data in REQUISITOS_ITSE:
        statement = select(Requisito).where(
            Requisito.nombre == req_data["nombre"],
            Requisito.aplica_a == req_data["aplica_a"]
        )
        existing = session.exec(statement).first()
        
        if not existing:
            requisito = Requisito(
                nombre=req_data["nombre"],
                descripcion=req_data["descripcion"],
                tipo_archivo_permitido=req_data["tipo_archivo_permitido"],
                es_obligatorio=req_data["es_obligatorio"],
                aplica_a=req_data["aplica_a"],
            )
            session.add(requisito)
            count_itse += 1
    
    session.commit()
    total = count_licencia + count_itse
    return total, count_licencia, count_itse


def seed_admin(session: Session) -> bool:
    existing_usuario = usuario_repository.get_by_email(session, ADMIN_CONFIG["correo_electronico"])
    
    if existing_usuario:
        return False
    
    hashed_password = get_password_hash(ADMIN_CONFIG["contrasena"])
    
    usuario = Usuario(
        correo_electronico=ADMIN_CONFIG["correo_electronico"],
        contrasena=hashed_password,
        rol=RolUsuario.GERENTE,
        fecha_creacion=datetime.now(timezone.utc),
        activo=True,
    )
    session.add(usuario)
    session.flush()
    
    empleado = Empleado(
        id_usuario=usuario.id,
        nombres=ADMIN_CONFIG["nombres"],
        apellidos=ADMIN_CONFIG["apellidos"],
        cargo=ADMIN_CONFIG["cargo"],
        area=ADMIN_CONFIG["area"],
    )
    session.add(empleado)
    session.commit()
    
    return True


def seed_all() -> Tuple[bool, str, int, bool]:
    try:
        from app.database.connection import _ensure_data_dir
        _ensure_data_dir()
        
        with Session(engine) as session:
            count_requisitos, _, _ = seed_requisitos(session)
            admin_creado = seed_admin(session)
        
        return True, "Datos cargados exitosamente", count_requisitos, admin_creado
    except Exception as e:
        return False, f"Error al cargar datos: {str(e)}", 0, False


if __name__ == "__main__":
    success, message, count, admin_created = seed_all()
    if success:
        exit(0)
    else:
        exit(1)
