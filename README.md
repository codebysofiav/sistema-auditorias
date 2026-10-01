# Sistema de Auditorias UIS

Aplicacion web interna para la gestion de auditorias de la Universidad Industrial de Santander (UIS). Integra un backend REST con Django y un frontend en Vue para administrar auditorias, planeacion, hallazgos, planes de mejoramiento, informes y usuarios.

## Stack

- Frontend: Vue 3 + Vite
- Backend: Django + Django REST Framework
- Autenticacion: JWT con Simple JWT (access 60 min, refresh 7 dias; el frontend renueva el access token automaticamente ante un 401)
- Documentacion API: drf-spectacular / Swagger UI
- Base de datos actual de desarrollo: SQLite
- Base de datos objetivo del proyecto: PostgreSQL (pendiente de configurar en el servidor)

## Estructura

```text
sistema-auditoria/
├── backend/
│   ├── auditorias/
│   │   └── management/commands/generar_alertas_vencimiento.py
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
- Autenticacion JWT por email, con renovacion automatica de access token desde el frontend.
- Endpoints de login, refresh, logout, usuario autenticado, creacion y listado de usuarios.
- API REST para las entidades principales de auditorias.
- Permisos por rol usando grupos de Django.
- Filtrado de querysets para que los auditores solo vean auditorias asignadas activas.
- CRUD de Unidades Auditadas para Administrador y Auditor, con borrado logico (`activo=False`) para no romper auditorias asociadas.
- Generacion automatica de alertas de vencimiento (2 dias antes de la fecha limite de una accion de mejoramiento) y marcado automatico de acciones vencidas, via management command.
- Documentacion automatica de API con drf-spectacular.
- Tests de permisos en `backend/auditorias/tests/test_permissions.py` (22 pruebas).
- Rol `Director`, con acceso completo a los recursos de auditorias y acceso restringido a la gestion de usuarios.
- Flujo de revision de informes preliminares: Director o Administrador pueden aprobar o solicitar correcciones; un Auditor que corrige y guarda un informe observado lo reenvia automaticamente a revision.
- Un informe definitivo solo puede crearse cuando existe un informe preliminar aprobado para la misma auditoria.

El frontend ya cuenta con:

- Vistas de Auditorias, Hallazgos, Informes, Documentos y Plan de mejoramiento.
- Modulo de Usuarios: listar, crear, editar y eliminar, disponible solo para Administrador.
- Modulo de Planeacion (plan de auditoria, cronograma, equipo auditor).
- Modulo de Unidades Auditadas (listar, crear, editar, desactivar).
- Panel de alertas en el sidebar, con conteo de no leidas y opcion de marcarlas como leidas.
- Resaltado de acciones proximas a vencer o vencidas en el detalle del plan de mejoramiento.

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
POST   /api/auth/login/
POST   /api/auth/refresh/
POST   /api/auth/logout/
GET    /api/auth/me/
GET    /api/auth/usuarios/
POST   /api/auth/usuarios/crear/
GET    /api/auth/usuarios/auditores/
GET    /api/auth/usuarios/<id>/
PATCH  /api/auth/usuarios/<id>/
DELETE /api/auth/usuarios/<id>/
```

### auditorias

Incluye ViewSets y rutas para:

```text
/api/unidades/                          # ?incluir_inactivas=true para ver las desactivadas
/api/auditorias/
/api/auditoria-auditores/
/api/informes/
/api/informes/<id>/revisar/             # POST: aprobar o solicitar correcciones
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
/api/notificaciones/no-leidas/          # alertas pendientes del usuario autenticado
/api/notificaciones/<id>/marcar-leida/  # POST
```

## Roles y Permisos

Los permisos principales estan implementados en `auditorias/permissions.py`.

Roles definidos:

- `Administrador`: acceso completo.
- `Director`: acceso completo a los recursos de auditorias, incluyendo la revision de informes; no puede gestionar usuarios.
- `Auditor`: puede consultar y modificar recursos asociados a auditorias donde esta asignado; puede crear, editar y desactivar Unidades Auditadas.
- `Usuario consulta`: solo lectura en todos los modulos.

Los ViewSets de `auditorias` heredan de un mixin que aplica `AuditoriaRolePermission` y filtra listados para evitar que un auditor vea informacion de auditorias ajenas.

## Alertas de vencimiento

Regla de negocio: una accion de mejoramiento genera una alerta 2 dias antes de su `fecha_limite` para cada auditor activo asignado a la auditoria; si vence sin completarse, se marca automaticamente con estado `Vencida`.

Se ejecuta con:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py generar_alertas_vencimiento
```

**Pendiente:** programar este comando para que corra a diario (Programador de tareas de Windows, o el mecanismo equivalente cuando el servidor pase a Linux/PostgreSQL). Hoy no es automatico.

La proteccion contra duplicados se aplica por combinacion de accion, usuario y tipo de alerta. Por tanto, cada auditor activo recibe una alerta propia sin duplicar alertas en ejecuciones posteriores.

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

Generar alertas de vencimiento:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py generar_alertas_vencimiento
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

## Pendiente antes del despliegue

1. Realizar la seccion del backend para la generacion de documentos con las plantillas institucionales.
2. Revisar que todas las variables utilizadas en los formularios se encuentren correctamente representadas y persistidas en la base de datos.
3. Realizar una revision integral de seguridad de la aplicacion.
4. Montar y configurar la base de datos compartida en el servidor con PostgreSQL.
5. Revisar y configurar que la aplicacion solo pueda abrirse desde la red interna de la Universidad.
6. Consultar con la Universidad si es posible vincular el correo institucional al inicio de sesion para habilitar recuperacion de contrasena por correo, sin depender de un usuario Administrador.

## Notas de Desarrollo

- La configuracion actual permite CORS desde `http://localhost:5173` para desarrollo.
- La autenticacion global de DRF usa JWT.
- El permiso global es `IsAuthenticated`; los ViewSets de auditorias aplican permisos especificos por rol y asignacion.
- No se debe exponer `password` ni hashes de contrasena en serializers de lectura.
- La base de datos configurada actualmente es SQLite; PostgreSQL sigue siendo el objetivo definido para despliegue o una etapa posterior.
