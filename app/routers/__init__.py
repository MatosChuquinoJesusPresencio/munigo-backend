from app.routers.auth import router as auth_router
from app.routers.tramites import router as tramites_router
from app.routers.evaluacion import router as evaluacion_router
from app.routers.citas import router as citas_router
from app.routers.inspecciones import router as inspecciones_router
from app.routers.notificaciones import router as notificaciones_router
from app.routers.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "tramites_router",
    "evaluacion_router",
    "citas_router",
    "inspecciones_router",
    "notificaciones_router",
    "dashboard_router",
]
