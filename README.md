# Sistema de Auditorias

Aplicacion web interna para la gestion de auditorias. El proyecto esta dividido en backend Django REST Framework y frontend Vue 3 + Vite.

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

El frontend ya cuenta con:

- Vistas de Auditorias, Hallazgos, Informes, Documentos y Plan de mejoramiento.
- Modulo de Usuarios (listar, crear; edicion y eliminacion agregadas — **confirmar endpoints exactos usados**, ver seccion Rutas mas abajo).
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
# TODO: documentar aqui las rutas de editar/eliminar usuario una vez confirmadas
```

### auditorias

Incluye ViewSets y rutas para:

```text
/api/unidades/                          # ?incluir_inactivas=true para ver las desactivadas
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
/api/notificaciones/no-leidas/          # alertas pendientes del usuario autenticado
/api/notificaciones/<id>/marcar-leida/  # POST
```

## Roles y Permisos

Los permisos principales estan implementados en `auditorias/permissions.py`.

Roles definidos:

- `Administrador`: acceso completo.
- `Auditor`: puede consultar y modificar recursos asociados a auditorias donde esta asignado; puede crear, editar y desactivar Unidades Auditadas.
- `Usuario consulta`: solo lectura en todos los modulos.

Los ViewSets de `auditorias` heredan de un mixin que aplica `AuditoriaRolePermission` y filtra listados para evitar que un auditor vea informacion de auditorias ajenas.

## Alertas de vencimiento

Regla de negocio: una accion de mejoramiento genera una alerta 2 dias antes de su `fecha_limite`; si vence sin completarse, se marca automaticamente con estado `Vencida`.

Se ejecuta con:

```powershell
cd backend
.\venv\Scripts\python.exe manage.py generar_alertas_vencimiento
```

**Pendiente:** programar este comando para que corra a diario (Programador de tareas de Windows, o el mecanismo equivalente cuando el servidor pase a Linux/PostgreSQL). Hoy no es automatico.

Nota: la alerta se asigna al primer auditor activo de la auditoria asociada, porque `AccionMejoramiento` no tiene un campo de responsable directo. Revisar si conviene notificar a todos los auditores activos en vez de solo al primero.

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

## Pendiente (en este orden)

1. **Gestion documental**: modelo de plantillas institucionales, variables dinamicas, motor de generacion de documentos (Word/PDF/Excel), y la regla de que el informe definitivo solo puede generarse despues de revisar el preliminar.
2. **PostgreSQL**: migrar la base de datos de desarrollo (SQLite) a PostgreSQL en el servidor.
3. **Interfaz**: mejoras de diseño general y barra de estados visual para las auditorias (hoy `estado` es texto libre, sin `choices` definidos en el modelo).

## Notas de Desarrollo

- La configuracion actual permite CORS desde `http://localhost:5173`.
- La autenticacion global de DRF usa JWT.
- El permiso global es `IsAuthenticated`; los ViewSets de auditorias aplican permisos especificos por rol y asignacion.
- No se debe exponer `password` ni hashes de contrasena en serializers de lectura.
- Los campos `estado` de `Auditoria` y `AccionMejoramiento` son texto libre (sin `choices` en el modelo); conviene formalizarlos al abordar la barra de estados.
- La base de datos configurada actualmente es SQLite; PostgreSQL sigue siendo el objetivo definido para despliegue o una etapa posterior.