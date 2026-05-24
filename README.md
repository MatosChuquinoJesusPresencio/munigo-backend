# MuniGo - Sistema de Gestión de Trámites Municipales

Sistema full-stack con **backend Python (POO)** y **frontend React** para automatizar la validación de requisitos y clasificación de trámites de Licencias de Funcionamiento e ITSE, optimizando los tiempos de respuesta municipal.

## Stack Tecnológico

- **Backend:** Python - Programación Orientada a Objetos (Abstracción, Encapsulamiento, Herencia, Polimorfismo)
- **Frontend:** React + Vite
- **API:** REST con FastAPI/Flask

## Módulos

| Módulo | Descripción |
|--------|-------------|
| **Gestión de Trámites** | Registro de usuarios, consulta de requisitos, carga documental, solicitud de citas |
| **Evaluación** | Validación de documentos, clasificación automática de riesgo (bajo/medio/alto), notificaciones de observaciones |
| **Inspección y Control** | Asignación de hoja de ruta para inspectores, registro de resultados de inspección |
| **Dashboard** | Reportes gerenciales con métricas de productividad y tiempos de atención (Recharts) |

## Roles del Sistema

- **Ciudadano** — Usuario final que gestiona sus trámites
- **Funcionario de Ventanilla** — Valida documentos y gestiona expedientes
- **Inspector Técnico ITSE** — Planifica rutas y registra inspecciones de campo
- **Gerente / Administrador** — Visualiza reportes y métricas operativas

## Problemática que Resuelve

- Alta tasa de retorno por documentación incompleta (3-4 visitas presenciales por trámite)
- Cuellos de botella al mezclar trámites de distinto nivel de riesgo en la misma cola
- Falta de trazabilidad del expediente para el ciudadano
- Opacidad en disponibilidad de inspectores y tiempos de atención

---

*Proyecto académico - Lenguajes de Programación*
