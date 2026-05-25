from enum import Enum


class UserRole(str, Enum):
    CIUDADANO = "ciudadano"
    FUNCIONARIO = "funcionario"
    INSPECTOR = "inspector"
    GERENTE = "gerente"


class RiskLevel(str, Enum):
    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"


class TramiteStatus(str, Enum):
    PENDIENTE = "pendiente"
    EN_REVISION = "en_revision"
    OBSERVADO = "observado"
    APROBADO_DOCUMENTOS = "aprobado_documentos"
    CITA_ASIGNADA = "cita_asignada"
    EN_INSPECCION = "en_inspeccion"
    INSPECCION_APROBADA = "inspeccion_aprobada"
    INSPECCION_RECHAZADA = "inspeccion_rechazada"
    FINALIZADO = "finalizado"
    RECHAZADO = "rechazado"


class Settings:
    APP_NAME: str = "MuniGo"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    SECRET_KEY: str = "lenguajes-de-programacion-24697-muni-go"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    
    DATABASE_URL: str = "sqlite:///./app/database/data/munigo.db"
    
    UPLOAD_DIR: str = "app/static/uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024


settings = Settings()
