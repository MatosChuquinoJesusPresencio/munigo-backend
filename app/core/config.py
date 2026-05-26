from enum import Enum


class RolUsuario(str, Enum):
    CIUDADANO = "ciudadano"
    FUNCIONARIO = "funcionario"
    INSPECTOR = "inspector"
    GERENTE = "gerente"


class NivelRiesgo(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class EstadoTramite(str, Enum):
    BORRADOR = "borrador"
    PENDIENTE_REVISION = "pendiente_revision"
    DOCUMENTOS_APROBADOS = "documentos_aprobados"
    PENDIENTE_INSPECCION = "pendiente_inspeccion"
    APROBADO = "aprobado"
    OBSERVADO = "observado"
    RECHAZADO = "rechazado"


class TipoTramite(str, Enum):
    LICENCIA_FUNCIONAMIENTO = "licencia_funcionamiento"
    ITSE = "itse"


class EstadoValidacion(str, Enum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    OBSERVADO = "observado"


class EstadoCita(str, Enum):
    PROGRAMADA = "programada"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class ResultadoInspeccion(str, Enum):
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    NO_APROBADO = "no_aprobado"


class TipoDocumento(str, Enum):
    DNI = "DNI"
    RUC = "RUC"
    CARNET_EXTRANJERIA = "carnet_extranjeria"
    PASAPORTE = "pasaporte"


class Settings:
    APP_NAME: str = "MuniGo"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    SQL_ECHO: bool = False
    
    SECRET_KEY: str = "lenguajes-de-programacion-24697-muni-go"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    DATABASE_URL: str = "sqlite:///./app/database/data/munigo.db"
    
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024


settings = Settings()
