from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database.scripts import setup_database
from app.routers import (
    auth_router,
    tramites_router,
    evaluacion_router,
    citas_router,
    inspecciones_router,
    notificaciones_router,
    dashboard_router,
)


app = FastAPI(
    title="MuniGo - Sistema de Gestión de Trámites Municipales",
    description="Sistema de gestión de trámites municipales para Licencias de Funcionamiento e ITSE",
    version="0.1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="app/static"), name="static")


templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def on_startup():
    setup_database()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/login.html"
    )


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="auth/register.html"
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "MuniGo está funcionando"}


app.include_router(auth_router)
app.include_router(tramites_router)
app.include_router(evaluacion_router)
app.include_router(citas_router)
app.include_router(inspecciones_router)
app.include_router(notificaciones_router)
app.include_router(dashboard_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
