from app.routers.auth_router import auth_router
from app.routers.tramites_router import tramites_router
from app.routers.evaluacion_router import evaluacion_router
from app.routers.citas_router import citas_router
from app.routers.inspecciones_router import inspecciones_router
from app.routers.notificaciones_router import notificaciones_router
from app.routers.dashboard_router import dashboard_router

__all__ = [
    "auth_router",
    "tramites_router",
    "evaluacion_router",
    "citas_router",
    "inspecciones_router",
    "notificaciones_router",
    "dashboard_router",
]
