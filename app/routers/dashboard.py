"""
Dashboard Router - FASE 2
==========================

Este router se implementará completamente en la Fase 2.
Por ahora incluye endpoints placeholder que devuelven mensajes informativos.

Funcionalidades Fase 2:
- Estadísticas generales
- Tiempo promedio de trámite
- Distribución por nivel de riesgo
- Rendimiento de funcionarios
- Expedientes con mayor tiempo de espera
- Alertas de expedientes vencidos
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.database.connection import get_session
from app.core.dependencies import (
    get_current_gerente_obj,
    get_current_funcionario_obj,
)
from app.models import Empleado
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard (Fase 2)"])


MENSAJE_FASE_2 = {
    "mensaje": "Esta funcionalidad estará disponible en la Fase 2",
    "estado": "placeholder",
    "fase_implementacion": 2
}


@router.get("/estadisticas")
def estadisticas_generales(
    fecha_inicio: Optional[date] = Query(None, description="Fecha de inicio"),
    fecha_fin: Optional[date] = Query(None, description="Fecha de fin"),
    _gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Estadísticas generales de trámites",
        "datos_previstos": [
            "total_expedientes",
            "aprobados",
            "rechazados",
            "pendientes",
            "tasa_aprobacion",
            "nuevos_este_mes"
        ]
    }


@router.get("/tiempo-promedio")
def tiempo_promedio_tramite(
    tipo_tramite: Optional[str] = Query(None, description="Filtrar por tipo de trámite"),
    _gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Tiempo promedio de trámite por tipo",
        "datos_previstos": [
            "promedio_dias_general",
            "por_tipo_tramite",
            "por_nivel_riesgo"
        ]
    }


@router.get("/distribucion-riesgo")
def distribucion_por_riesgo(
    _gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Distribución de expedientes por nivel de riesgo",
        "datos_previstos": [
            "bajo: {cantidad, porcentaje}",
            "medio: {cantidad, porcentaje}",
            "alto: {cantidad, porcentaje}"
        ]
    }


@router.get("/rendimiento-funcionarios")
def rendimiento_funcionarios(
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    _gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Rendimiento de funcionarios",
        "datos_previstos": [
            "expedientes_revisados",
            "tiempo_promedio_revision",
            "tasa_aprobacion",
            "tasa_observacion"
        ]
    }


@router.get("/expedientes-lentos")
def expedientes_lentos(
    limite: int = Query(10, ge=1, le=100, description="Cantidad de expedientes a mostrar"),
    _gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Expedientes con mayor tiempo de espera",
        "datos_previstos": [
            "id_expediente",
            "codigo_seguimiento",
            "estado_actual",
            "dias_en_estado",
            "tipo_tramite",
            "nivel_riesgo"
        ]
    }


@router.get("/alertas-vencidos")
def alertas_vencidos(
    dias_vencimiento: int = Query(15, ge=1, description="Días límite según normativa"),
    _gerente: Empleado = Depends(get_current_gerente_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Alertas de expedientes vencidos o próximos a vencer",
        "datos_previstos": [
            "vencidos",
            "proximos_a_vencer",
            "total_vencidos",
            "total_proximos"
        ],
        "nota": "Considerará días hábiles según normativa municipal"
    }


@router.get("/resumen")
def resumen_rapido(
    _empleado: Empleado = Depends(get_current_funcionario_obj),
    session: Session = Depends(get_session)
):
    return {
        **MENSAJE_FASE_2,
        "funcionalidad": "Resumen rápido para el dashboard principal",
        "datos_previstos": [
            "pendientes_hoy",
            "vencimientos_proximos",
            "mis_pendientes",
            "ultimas_actualizaciones"
        ]
    }
