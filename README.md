# MuniGo - Sistema de Gestión de Trámites Municipales

Sistema de gestión de trámites municipales para **Licencias de Funcionamiento** e **Inspecciones Técnicas de Seguridad en Edificaciones (ITSE)**. Desarrollado con **Python + FastAPI (POO)** y **HTML + Jinja2 + HTMX**.

**Proyecto académico - Curso de Lenguajes de Programación**

---

## 🎯 Problemática que Resuelve

1. **Ping-Pong burocrático** - Ciudadano asiste 3-4 veces por trámite por documentación incompleta
2. **Cuellos de botella** - Trámites de distinto riesgo en la misma cola
3. **Incertidumbre** - Sin información sobre disponibilidad de inspectores
4. **Opacidad** - Sin seguimiento del estado del expediente

---

## 🛠️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python + FastAPI |
| **Frontend** | HTML + Jinja2 (templates) + HTMX |
| **Charts** | Chart.js |
| **Paradigma** | Programación Orientada a Objetos (POO) |

---

## ✅ Características Principales

- **Validación previa de documentos** - Evita el "ping-pong burocrático"
- **Clasificación automática de riesgo** - Bajo / Medio / Alto según giro y tamaño
- **Sistema de citas** - Horario programado para atención presencial
- **Trazabilidad del expediente** - Seguimiento visual del estado del trámite
- **Inspecciones técnicas** - Solo para trámites de Riesgo Alto
- **Roles diferenciados** - Ciudadano, Funcionario, Inspector, Gerente

---

## 👥 Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| **Ciudadano** | Usuario final - Registra trámites, carga documentos, solicita citas, sigue el estado |
| **Funcionario de Ventanilla** | Valida documentos, aprueba u observa expedientes |
| **Inspector Técnico ITSE** | Gestiona hoja de ruta, registra resultados de inspección (solo Riesgo Alto) |
| **Gerente / Administrador** | Visualiza reportes y métricas operativas |

---

## 📊 Niveles de Riesgo

| Nivel | Descripción | Requiere Inspección |
|-------|-------------|---------------------|
| **Bajo** | Giro común + < 100 m² | ❌ No |
| **Medio** | Giro común + 100-500 m² | ❌ No |
| **Alto** | Giro especial (Restaurante, Discoteca, Centro Comercial, etc.) | ✅ Sí |

---

## 🚀 Instalación y Ejecución

```bash
# Clonar el repositorio
git clone https://github.com/MatosChuquinoJesusPresencio/sgtm-muni-go.git
cd sgtm-muni-go

# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
uvicorn app.main:app --reload
```

---

## 📁 Estructura del Proyecto

```
sgtm-muni-go/
├── app/
│   ├── main.py                 # Entry point FastAPI
│   ├── core/                   # Configuración, seguridad, dependencias
│   ├── database/               # Archivo SQLite + conexión BD
│   ├── models/                 # Clases OOP / SQLAlchemy models
│   ├── schemas/                # Pydantic - Validación de datos entrada/salida
│   ├── repositories/           # Data Access Layer (consultas BD)
│   ├── services/               # Lógica de negocio
│   ├── routers/                # Rutas FastAPI
│   ├── templates/              # Jinja2 HTML
│   └── static/                 # CSS, JS, uploads
├── .gitignore
├── requirements.txtUn
└── README.md
```