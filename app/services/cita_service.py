from typing import List, Optional
from datetime import date, time, datetime
from sqlmodel import Session

from app.core.config import EstadoTramite, EstadoCita
from app.models import Expediente, Cita
from app.repositories import (
    expediente_repository,
    cita_repository,
    empleado_repository
)
from app.schemas import (
    CitaCreate,
    CitaUpdate,
    CitaAsignarRequest
)


class CitaService:
    HORA_INICIO_OFICINA = time(8, 0)
    HORA_FIN_OFICINA = time(17, 0)
    DURACION_CITA_MINUTOS = 60

    @staticmethod
    def _es_dia_habil(fecha: date) -> bool:
        return fecha.weekday() < 5

    @staticmethod
    def _generar_horarios_disponibles() -> List[dict]:
        horarios = []
        hora_actual = datetime(2000, 1, 1, CitaService.HORA_INICIO_OFICINA.hour, 0)
        fin_oficina = datetime(2000, 1, 1, CitaService.HORA_FIN_OFICINA.hour, 0)
        
        while hora_actual < fin_oficina:
            hora_fin = hora_actual.replace(minute=CitaService.DURACION_CITA_MINUTOS)
            if hora_fin > fin_oficina:
                break
            
            horarios.append({
                "hora_inicio": hora_actual.time(),
                "hora_fin": hora_fin.time()
            })
            hora_actual = hora_fin
        
        return horarios

    @staticmethod
    def obtener_horarios_disponibles(
        session: Session,
        fecha: date
    ) -> List[dict]:
        if not CitaService._es_dia_habil(fecha):
            return []
        
        horarios_disponibles = CitaService._generar_horarios_disponibles()
        
        from sqlmodel import select
        statement = select(Cita).where(
            Cita.fecha == fecha,
            Cita.estado == EstadoCita.PROGRAMADA
        )
        citas_existentes = session.exec(statement).all()
        
        horarios_ocupados = set()
        for cita in citas_existentes:
            horarios_ocupados.add((cita.hora_inicio, cita.hora_fin))
        
        horarios_libres = []
        for horario in horarios_disponibles:
            if (horario["hora_inicio"], horario["hora_fin"]) not in horarios_ocupados:
                horarios_libres.append(horario)
        
        return horarios_libres

    @staticmethod
    def programar_cita(
        session: Session,
        cita_data: CitaAsignarRequest,
        id_funcionario: Optional[int] = None
    ) -> Cita:
        expediente = expediente_repository.get_by_id(session, cita_data.id_expediente)
        if not expediente:
            raise ValueError("Expediente no encontrado")
        
        if expediente.estado != EstadoTramite.PENDIENTE_INSPECCION:
            raise ValueError("Solo se pueden programar citas para expedientes en PENDIENTE_INSPECCION")
        
        if not CitaService._es_dia_habil(cita_data.fecha):
            raise ValueError("Solo se pueden programar citas en días hábiles (Lunes-Viernes)")
        
        horarios_disponibles = CitaService.obtener_horarios_disponibles(session, cita_data.fecha)
        horario_solicitado = {
            "hora_inicio": cita_data.hora_inicio,
            "hora_fin": cita_data.hora_fin
        }
        
        if horario_solicitado not in horarios_disponibles:
            raise ValueError("El horario solicitado no está disponible")
        
        cita_create = CitaCreate(
            id_expediente=cita_data.id_expediente,
            id_funcionario=id_funcionario,
            fecha=cita_data.fecha,
            hora_inicio=cita_data.hora_inicio,
            hora_fin=cita_data.hora_fin
        )
        
        cita = Cita(
            id_expediente=cita_create.id_expediente,
            id_funcionario=cita_create.id_funcionario,
            fecha=cita_create.fecha,
            hora_inicio=cita_create.hora_inicio,
            hora_fin=cita_create.hora_fin,
            estado=EstadoCita.PROGRAMADA
        )
        
        return cita_repository.create(session, cita)

    @staticmethod
    def obtener_cita(
        session: Session,
        cita_id: int
    ) -> Optional[Cita]:
        return cita_repository.get_by_id(session, cita_id)

    @staticmethod
    def obtener_citas_expediente(
        session: Session,
        id_expediente: int
    ) -> List[Cita]:
        from sqlmodel import select
        statement = select(Cita).where(
            Cita.id_expediente == id_expediente
        ).order_by(Cita.fecha.desc())
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def obtener_citas_funcionario(
        session: Session,
        id_funcionario: int
    ) -> List[Cita]:
        from sqlmodel import select
        statement = select(Cita).where(
            Cita.id_funcionario == id_funcionario,
            Cita.estado == EstadoCita.PROGRAMADA
        ).order_by(Cita.fecha, Cita.hora_inicio)
        results = session.exec(statement)
        return list(results.all())

    @staticmethod
    def cancelar_cita(
        session: Session,
        cita_id: int,
        motivo: str = ""
    ) -> Optional[Cita]:
        cita = cita_repository.get_by_id(session, cita_id)
        if not cita:
            return None
        
        if cita.estado != EstadoCita.PROGRAMADA:
            raise ValueError("Solo se pueden cancelar citas programadas")
        
        update_data = CitaUpdate(estado=EstadoCita.CANCELADA)
        return cita_repository.update(session, cita, update_data)

    @staticmethod
    def completar_cita(
        session: Session,
        cita_id: int
    ) -> Optional[Cita]:
        cita = cita_repository.get_by_id(session, cita_id)
        if not cita:
            return None
        
        if cita.estado != EstadoCita.PROGRAMADA:
            raise ValueError("Solo se pueden completar citas programadas")
        
        update_data = CitaUpdate(estado=EstadoCita.COMPLETADA)
        return cita_repository.update(session, cita, update_data)


cita_service = CitaService()
