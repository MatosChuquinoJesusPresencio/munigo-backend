# MuniGO — Backend API

API REST para el sistema de gestión de trámites y citas municipales del Area de Desarrollo Económico y la Subgerencia de Comercialización de los Olivos.

## Stack

- **Python** 3.10
- **Django** 5.2.16
- **Django REST Framework** 3.17.1
- **SimpleJWT** 5.5.1 (autenticación JWT)
- **PostgreSQL** (Supabase) via psycopg2
- **Gunicorn** (servidor WSGI en producción)
- **ReportLab** (generación de PDFs de licencias)

## Estructura del proyecto

```
munigo-backend/
├── config/                 # Configuración de Django (settings, urls, wsgi)
├── users/                  # Autenticación, usuarios, empleados
├── organizations/          # Empresas, establecimientos, categorías
├── procedures/             # Expedientes, requisitos, documentos, citas
│   └── pdf_generator.py    # Generación de PDF de licencias de funcionamiento
├── notifications/          # Notificaciones a ciudadanos
├── inspections/            # Inspecciones de campo
├── db/
│   └── seed.sql            # Datos iniciales (usuarios, empresas, requisitos)
├── manage.py
├── requirements.txt
└── Dockerfile
```

### Apps de Django

| App | Descripción |
|-----|-------------|
| `users` | Modelos de usuario (User, Citizen, Employee), autenticación JWT, CRUD de empleados |
| `organizations` | Empresas (con RUC), establecimientos, categorías de negocio, matriz de riesgo |
| `procedures` | Expedientes, requisitos, documentos adjuntos, citas, validación documental |
| `notifications` | Notificaciones para ciudadanos en cada cambio de estado |
| `inspections` | Registros de inspección de campo con resultado y fotos |

## Modelos principales

### users

| Modelo | Campos clave | Relaciones |
|--------|-------------|------------|
| **User** | `role` (CITIZEN/EMPLOYEE) | Extiende AbstractUser |
| **Citizen** | `document_type`, `document_number` (único) | OneToOne → User |
| **Employee** | `position` (GERENTE/INSPECTOR/FUNCIONARIO), `area` | OneToOne → Citizen |
| **BlacklistedToken** | `token`, `blacklisted_at` | — |

### organizations

| Modelo | Campos clave | Relaciones |
|--------|-------------|------------|
| **Company** | `business_name`, `ruc` (13 dígitos, único) | ManyToMany → Citizen |
| **Establishment** | `name`, `address`, `business_category`, `square_meters` | FK → Company |
| **BusinessCategory** | RESTAURANT, COMERCIO, ALMACEN, SERVICIOS, INDUSTRIA | — |

### procedures

| Modelo | Campos clave | Relaciones |
|--------|-------------|------------|
| **CaseFile** | `tracking_code` (EXP-XXXXXXXX), `procedure_type`, `risk_level`, `status` | FK → Citizen, FK → Establishment |
| **Requirement** | `name`, `description`, `allowed_formats`, `is_required` | — |
| **ProcedureRequirement** | `fulfilled` | FK → CaseFile, FK → Requirement |
| **AttachedDocument** | `name`, `file` (URL), `validation_status`, `observations` | FK → ProcedureRequirement |
| **Appointment** | `scheduled_date`, `start_time`, `end_time`, `status`, `notes`, `cancel_reason` | FK → CaseFile, FK → Employee (inspector, created_by) |

### notifications

| Modelo | Campos clave | Relaciones |
|--------|-------------|------------|
| **Notification** | `title`, `message`, `is_read`, `sent_at` | FK → Citizen, FK → CaseFile |

### inspections

| Modelo | Campos clave | Relaciones |
|--------|-------------|------------|
| **Inspection** | `result` (APROBADO/NO_APROBADO), `comments`, `photo_urls` | OneToOne → Appointment |

## Autenticación

El sistema usa **JWT** (JSON Web Tokens) con SimpleJWT:

- **Access token**: 1 hora de duración
- **Refresh token**: 7 días de duración
- **Rotación**: Los refresh tokens se rotan en cada uso
- **Blacklist**: Los refresh tokens se invalidan al cerrar sesión

### Login por documento

El backend usa un `DocumentBackend` personalizado que permite autenticarse con **tipo de documento + número de documento + contraseña** (no se usa email para login).

### Headers requeridos

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

## Roles y permisos

| Rol | Carga | Permisos |
|-----|-------|----------|
| **Ciudadano** | Registra empresa, crea expedientes, sube documentos, confirma/cancela/reprograma citas, descarga licencia aprobada |
| **Funcionario** | Revisa documentos, asigna inspectores, agenda citas, ve dashboard |
| **Inspector** | Realiza inspecciones de campo, ve sus inspecciones y calendario |
| **Gerente** | Todo lo del Funcionario + gestiona empleados (CRUD) y requisitos |

### Permisos personalizados

- `IsGerente` — Solo empleados con `position == GERENTE`
- `IsEmployee` — Solo usuarios que tengan un perfil de empleado asociado

## API Endpoints

### Autenticación (`/api/auth/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| POST | `/api/auth/register/` | Registrar ciudadano | Público |
| POST | `/api/auth/login/` | Login (retorna JWT) | Público |
| POST | `/api/auth/logout/` | Logout (invalida refresh token) | Autenticado |
| POST | `/api/auth/refresh/` | Renovar access token | Público |
| GET | `/api/auth/me/` | Perfil del usuario actual | Autenticado |
| GET | `/api/auth/employees/` | Listar empleados | Gerente |
| POST | `/api/auth/employees/` | Crear empleado | Gerente |
| GET | `/api/auth/employees/{id}/` | Detalle de empleado | Gerente |
| PUT | `/api/auth/employees/{id}/` | Actualizar empleado | Gerente |
| DELETE | `/api/auth/employees/{id}/` | Eliminar empleado | Gerente |

### Organizaciones (`/api/organizations/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET/POST | `/api/organizations/companies/` | Listar/crear empresas | Autenticado |
| GET/PUT/DEL | `/api/organizations/companies/{id}/` | CRUD empresa | Autenticado |
| GET | `/api/organizations/companies/search/?q=` | Buscar empresa por nombre o RUC | Autenticado |
| POST | `/api/organizations/companies/{id}/add_citizen/` | Agregar ciudadano a empresa | Autenticado |
| POST | `/api/organizations/companies/{id}/remove_citizen/` | Remover ciudadano de empresa | Autenticado |
| GET/POST | `/api/organizations/establishments/` | Listar/crear establecimientos | Autenticado |
| GET/PUT/DEL | `/api/organizations/establishments/{id}/` | CRUD establecimiento | Autenticado |

### Expedientes (`/api/procedures/case-files/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET/POST | `/api/procedures/case-files/` | Listar/crear expedientes | Autenticado |
| GET/PUT/DEL | `/api/procedures/case-files/{id}/` | CRUD expediente | Autenticado |
| POST | `/api/procedures/case-files/{id}/submit/` | Enviar a revisión (BORRADOR → PENDIENTE_REVISION) | Ciudadano |
| GET | `/api/procedures/case-files/pending-review/` | Expedientes pendientes de revisión | Empleado |
| GET | `/api/procedures/case-files/history/` | Historial de expedientes | Empleado |
| GET | `/api/procedures/case-files/dashboard/` | Estadísticas (total, por estado, por tipo) | Empleado |
| POST | `/api/procedures/case-files/{id}/approve-documents/` | Aprobar documentos (→ DOCUMENTOS_APROBADOS) | Empleado |
| POST | `/api/procedures/case-files/{id}/assign-inspector/` | Asignar inspector y crear cita | Funcionario/Gerente |
| POST | `/api/procedures/case-files/{id}/set-status/` | Cambiar estado (APROBADO/OBSERVADO/RECHAZADO) | Empleado |
| GET | `/api/procedures/case-files/my-inspections/` | Mis inspecciones asignadas | Inspector |
| GET | `/api/procedures/case-files/inspection-history/` | Historial de inspecciones | Inspector |
| POST | `/api/procedures/case-files/{id}/complete-inspection/` | Completar inspección | Inspector |
| GET | `/api/procedures/case-files/{id}/download-license/` | Descargar licencia PDF (solo APROBADO) | Autenticado |

### Requisitos (`/api/procedures/requirements/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET/POST | `/api/procedures/requirements/` | Listar/crear requisitos | GET: Autenticado / POST: Gerente |
| GET/PUT/DEL | `/api/procedures/requirements/{id}/` | CRUD requisito | GET: Autenticado / PUT/DEL: Gerente |

### Documentos adjuntos (`/api/procedures/attached-documents/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET/POST | `/api/procedures/attached-documents/` | Listar/subir documentos | Autenticado |
| GET/PUT/DEL | `/api/procedures/attached-documents/{id}/` | CRUD documento | Autenticado |
| PATCH | `/api/procedures/attached-documents/{id}/validate/` | Validar documento (APROBADO/OBSERVADO) | Empleado |

### Citas (`/api/procedures/appointments/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET | `/api/procedures/appointments/` | Listar citas | Autenticado |
| GET | `/api/procedures/appointments/{id}/` | Detalle de cita | Autenticado |
| POST | `/api/procedures/appointments/{id}/confirm/` | Confirmar cita | Ciudadano |
| POST | `/api/procedures/appointments/{id}/cancel/` | Cancelar cita (requiere motivo) | Ciudadano/Empleado |
| POST | `/api/procedures/appointments/{id}/reschedule/` | Solicitar reprogramación | Ciudadano |
| POST | `/api/procedures/appointments/{id}/respond-reschedule/` | Aceptar/rechazar reprogramación | Empleado |
| GET | `/api/procedures/appointments/available-slots/?inspector_id=&date=` | Horarios disponibles | Autenticado |
| GET | `/api/procedures/appointments/calendar/?start=&end=&inspector_id=` | Vista calendario | Empleado |

### Notificaciones (`/api/notifications/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET | `/api/notifications/` | Listar notificaciones | Autenticado |
| GET | `/api/notifications/{id}/` | Detalle de notificación | Autenticado |
| POST | `/api/notifications/{id}/mark_as_read/` | Marcar como leída | Autenticado |
| POST | `/api/notifications/mark_all_as_read/` | Marcar todas como leídas | Autenticado |

### Inspecciones (`/api/inspections/`)

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|--------|
| GET/POST | `/api/inspections/` | Listar/crear inspecciones | Empleado |
| GET/PUT/DEL | `/api/inspections/{id}/` | CRUD inspección | Empleado |

### Salud

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Health check (retorna `{"status": "ok"}`) |
| GET | `/favicon.ico` | Retorna 204 |

## Flujo de estados

### Expediente (CaseFile)

```
BORRADOR → PENDIENTE_DE_REVISION → DOCUMENTOS_APROBADOS → PENDIENTE_DE_INSPECCION → APROBADO
                                                ↑                                      ↓
                                                │                                OBSERVADO
                                                │                                      ↓
                                                └──────────────────────────── RECHAZADO
```

**Transiciones:**
1. **BORRADOR → PENDIENTE_DE_REVISION**: Ciudadano envía (`submit`). Valida que todos los requisitos obligatorios estén cumplidos.
2. **PENDIENTE_DE_REVISION → DOCUMENTOS_APROBADOS**: Empleado aprueba documentos (`approve-documents`). Valida que todos los documentos obligatorios estén aprobados.
3. **DOCUMENTOS_APROBADOS → PENDIENTE_DE_INSPECCION**: Se produce automáticamente cuando el ciudadano **confirma** una cita asignada.
4. **PENDIENTE_DE_INSPECCION → APROBADO/OBSERVADO/RECHAZADO**: Inspector completa inspección o empleado cambia estado manualmente (`set-status`).

### Cita (Appointment)

```
PENDIENTE_CONFIRMACION → CONFIRMADA → COMPLETADA
        ↓                    ↓
   CANCELADA           PENDIENTE_REPROGRAMACION → CONFIRMADA (aceptada) / CANCELADA (rechazada)
        ↓
   CANCELADA
```

**Transiciones:**
1. **PENDIENTE_CONFIRMACION → CONFIRMADA**: Ciudadano confirma la cita.
2. **PENDIENTE_CONFIRMACION → CANCELADA**: Ciudadano cancela la cita (requiere motivo).
3. **CONFIRMADA → PENDIENTE_REPROGRAMACION**: Ciudadano solicita reprogramar.
4. **PENDIENTE_REPROGRAMACION → CONFIRMADA**: Funcionario acepta la reprogramación (actualiza fecha/hora).
5. **PENDIENTE_REPROGRAMACION → CANCELADA**: Funcionario rechaza la reprogramación.
6. **CONFIRMADA → COMPLETADA**: Inspector completa la inspección.

## Matriz de riesgo

El nivel de riesgo se calcula automáticamente al crear un expediente, combinando la **categoría de negocio** con el **tamaño** del establecimiento (según metros cuadrados):

| Categoría | Pequeño (≤50m²) | Mediano (51-200m²) | Grande (>200m²) |
|-----------|------------------|---------------------|------------------|
| RESTAURANT | MEDIO | ALTO | ALTO |
| COMERCIO | BAJO | MEDIO | ALTO |
| ALMACEN | MEDIO | ALTO | ALTO |
| SERVICIOS | BAJO | BAJO | MEDIO |
| INDUSTRIA | ALTO | ALTO | ALTO |

**Tamaño del establecimiento:**
- Pequeño: ≤ 50 m²
- Mediano: 51 - 200 m²
- Grande: > 200 m²

## Variables de entorno

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `DJANGO_SECRET_KEY` | Clave secreta de Django | Sí | — |
| `DEBUG` | Modo depuración | No | `False` |
| `ALLOWED_HOSTS` | Hosts permitidos (separados por coma) | No | `localhost,127.0.0.1` |
| `DATABASE_URL` | URL de conexión a PostgreSQL (Supabase) | No | SQLite local |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS permitidos (separados por coma) | No | `http://localhost:5173` |
| `PORT` | Puerto del servidor (para Railway) | No | `8000` |

> **Nota:** En producción se usa el pooler de Supabase (IPv4) ya que Railway requiere conexiones IPv4.

## Instalación local

```bash
# 1. Crear entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
copy .env.example .env         # Editar con tus valores

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Crear superusuario (opcional)
python manage.py createsuperuser

# 6. Cargar datos iniciales (opcional)
psql -U postgres -d munigo -f db/seed.sql

# 7. Iniciar servidor de desarrollo
python manage.py runserver 8080
```

El servidor estará disponible en `http://localhost:8080/api/`.

## Docker

```bash
# Construir imagen
docker build -t munigo-backend .

# Ejecutar
docker run -p 8000:8000 --env-file .env munigo-backend
```

El Dockerfile usa Python 3.10-slim, ejecuta `migrate --noinput` durante el build y sirve con Gunicorn en el puerto configurado por `$PORT` (default 8000).

## Seed data

El archivo `db/seed.sql` contiene datos iniciales para probar el sistema:

### Usuarios (contraseña: `admin123`)

| Username | Nombre | Rol | Posición | Área | DNI |
|----------|--------|-----|----------|------|-----|
| `admin` | Admin Munigo | EMPLOYEE | — | — | — |
| `ciudadano1` | Juan Perez | CITIZEN | — | — | 0102030405 |
| `ciudadano2` | Maria Lopez | CITIZEN | — | — | 0506070809 |
| `gerente` | Carlos Garcia | EMPLOYEE | GERENTE | ADMINISTRACION | 09999999990 |
| `inspector` | Ana Torres | EMPLOYEE | INSPECTOR | FISCALIZACION | 0105060708 |
| `funcionario` | Luis Martinez | EMPLOYEE | FUNCIONARIO | LICENCIAS | 0106070809 |

### Empresas y establecimientos

| Empresa | RUC | Establecimiento | Dirección | Categoría | m² |
|---------|-----|-----------------|-----------|-----------|-----|
| Restaurante El Sabor | 09912345671 | El Sabor - Sede Central | Av. 9 de Octubre 123, Guayaquil | RESTAURANT | 120 |
| Comercial TodoFarma | 09976543210 | TodoFarma - Centro | Calle Largo 456, Guayaquil | COMERCIO | 80 |
| Comercial TodoFarma | 09976543210 | TodoFarma - Norte | Av. Francisco de Orellana 789, Guayaquil | COMERCIO | 250 |

### Requisitos (catálogo)

**Licencia de Funcionamiento** (5): Planos de distribución, Certificado de zonificación, Póliza de responsabilidad civil, Fotografía del local, Pago de derechos municipales

**ITSE** (3): Certificado ITSE vigente, Plan de emergencia, Capacitación de personal (opcional)
