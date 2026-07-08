import random
import string
from datetime import datetime

from .models import Record, RiskLevel


class TramiteService:
    GIROS_ALTO_RIESGO = [
        "discoteca", "club nocturno", "bar", "pub", "cantina",
        "gasolinera", "estacion de servicio", "estación de servicio",
        "almacen peligroso", "almacén peligroso",
        "bodega quimicos", "bodega químicos",
        "hospital", "clinica", "clínica", "laboratorio",
    ]

    GIROS_MEDIO_RIESGO = [
        "restaurante", "cafeteria", "cafetería", "hotel",
        "centro comercial", "tienda departamental",
        "gimnasio", "spa",
    ]

    GIROS_BAJO_RIESGO = [
        "oficina", "consultorio", "estudio",
        "tienda pequena", "tienda pequeña", "panaderia", "panadería",
        "papeleria", "papelería", "bodega",
    ]

    ACENTOS = str.maketrans({
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N',
    })

    @staticmethod
    def generar_codigo():
        prefijo = "EXP-"
        fecha = datetime.now().strftime("%Y%m")
        aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefijo}{fecha}-{aleatorio}"

    @staticmethod
    def _normalizar(texto: str) -> str:
        return texto.translate(TramiteService.ACENTOS).lower()

    @classmethod
    def clasificar_riesgo(cls, business_type: str, premises_size: int) -> str:
        giro_norm = cls._normalizar(business_type)

        for palabra in cls.GIROS_ALTO_RIESGO:
            if cls._normalizar(palabra) in giro_norm:
                return RiskLevel.HIGH

        for palabra in cls.GIROS_MEDIO_RIESGO:
            palabra_norm = cls._normalizar(palabra)
            if palabra_norm in giro_norm:
                if "restaurante" in palabra_norm and premises_size > 200:
                    return RiskLevel.HIGH
                if "restaurante" in palabra_norm:
                    return RiskLevel.MEDIUM
                if ("cafe" in palabra_norm or "panaderia" in palabra_norm) and premises_size <= 100:
                    return RiskLevel.LOW
                return RiskLevel.MEDIUM

        for palabra in cls.GIROS_BAJO_RIESGO:
            if cls._normalizar(palabra) in giro_norm:
                return RiskLevel.LOW

        if premises_size > 500:
            return RiskLevel.HIGH
        elif premises_size > 200:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    @staticmethod
    def requiere_inspeccion(risk_level: str) -> bool:
        return risk_level == RiskLevel.HIGH

    @classmethod
    def get_risk_motive(cls, risk_level: str) -> str:
        motivos = {
            RiskLevel.LOW: "Riesgo bajo según giro y tamaño del local",
            RiskLevel.MEDIUM: "Riesgo medio según giro y tamaño del local",
            RiskLevel.HIGH: "Riesgo alto - requiere inspección obligatoria según giro o tamaño",
        }
        return motivos.get(risk_level, "Clasificación estándar")


tramite_service = TramiteService()
