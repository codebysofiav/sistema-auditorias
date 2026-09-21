# Sistema de Auditorias

Aplicacion web interna para la gestion de auditorias. El proyecto esta dividido en backend Django REST Framework y frontend Vue 3 + Vite.

## Stack

- Frontend: Vue 3 + Vite
- Backend: Django + Django REST Framework
- Autenticacion: JWT con Simple JWT
- Documentacion API: drf-spectacular / Swagger UI
- Base de datos actual de desarrollo: SQLite
- Base de datos objetivo del proyecto: PostgreSQL

## Estructura

```text
sistema-auditoria/
├── backend/
│   ├── auditorias/
│   ├── config/
│   ├── usuarios/
│   ├── manage.py
│   ├── requirements.txt
│   └── schema.yml
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── docs/
│   ├── base-datos/
│   └── diagramas/
├── README.md
└── LICENSE
```

## Estado Actual

El backend ya cuenta con:

- Modelo personalizado de usuario en la app `usuarios`.
- Autenticacion JWT por email.
- Endpoints de login, refresh, logout y usuario autenticado.
- Endpoint para crear usuarios desde el frontend.
- API REST para las entidades principales de auditorias.
- Permisos por rol usando grupos de Django.
- Filtrado de querysets para que los auditores solo vean auditorias asignadas activas.
- Documentacion automatica de API con drf-spectacular.
- Tests de permisos en `backend/auditorias/tests/test_permissions.py`.

El frontend existe como proyecto Vue 3 + Vite y ya tiene dependencias base como `axios`, `pinia` y `vue-router`.

## Apps del Backend

### usuarios

Incluye:

- `Usuario`, modelo personalizado basado en email.
- Serializer de login JWT.
- Serializer de creacion de usuarios.
- Serializer de lectura para `/api/auth/me/`.
- Registro del modelo en Django Admin usando `UserAdmin`.

Rutas:

```text
POST /api/auth/login/
POST /api/auth/refresh/
POST /api/auth/logout/
GET  /api/auth/me/
POST /api/auth/usuarios/crear/
```

### auditorias

Incluye ViewSets y rutas para:

```text
/api/unidades/
/api/auditorias/
/api/auditoria-auditores/
/api/informes/
/api/hallazgos/
/api/planes-auditoria/
/api/oportunidades-mejora/
/api/cronogramas/
/api/historial-cambios/
/api/planes-mejoramiento/
/api/acciones-mejoramiento/
/api/seguimientos/
/api/documentos/
/api/notificaciones/
```

## Roles y Permisos

Los permisos principales estan implementados en `auditorias/permissions.py`.

Roles definidos:

- `Administrador`: acceso completo.
- `Auditor`: puede consultar y modificar recursos asociados a auditorias donde esta asignado.
- `Usuario consulta`: solo lectura.

Los ViewSets de `auditorias` heredan de un mixin que aplica `AuditoriaRolePermission` y filtra listados para evitar que un auditor vea informacion de auditorias ajenas.

## Documentacion de API

La API expone documentacion con drf-spectacular:

```text
GET /api/schema/
GET /api/docs/
```

Para generar y validar el schema:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py spectacular --file schema.yml --validate
```

## Comandos Backend

Instalar dependencias:

```powershell
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Verificar configuracion:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py check
```

Ver migraciones:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py showmigrations
```

Ejecutar servidor:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py runserver
```

Ejecutar tests de permisos:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py test auditorias.tests.test_permissions --verbosity=2
```

## Comandos Frontend

Instalar dependencias:

```powershell
cd frontend
npm install
```

Ejecutar entorno de desarrollo:

```powershell
cd frontend
npm run dev
```

Construir para produccion:

```powershell
cd frontend
npm run build
```

## Notas de Desarrollo

- La configuracion actual permite CORS desde `http://localhost:5173`.
- La autenticacion global de DRF usa JWT.
- El permiso global es `IsAuthenticated`; los ViewSets de auditorias aplican permisos especificos por rol y asignacion.
- No se debe exponer `password` ni hashes de contrasena en serializers de lectura.
- La base de datos configurada actualmente es SQLite; PostgreSQL sigue siendo el objetivo definido para despliegue o una etapa posterior.
