# TodoApp Backend

API REST en Django para una app de tableros tipo Trello/Jira (Board → Sprint → Task → Comment), pensada como backend para una app móvil. Este README explica cómo está armado el backend y, al final, relaciona cada decisión de diseño con las guías de estudio de "Aplicaciones Móviles" (semanas 1 a 12) que motivaron los cambios.

## Stack

- **Django 6** + **Django REST Framework** — API
- **PostgreSQL** — base de datos
- **djangorestframework-simplejwt** — autenticación JWT (+ blacklist de refresh tokens)
- **drf-spectacular** — documentación OpenAPI (Swagger / Redoc)
- **django-filter** — filtrado de listados
- **django-cors-headers** — CORS para clientes móviles/Expo
- **Pydantic** — DTOs de validación entre la capa de API y los servicios

## Cómo correr el proyecto

```bash
make build          # Build de las imágenes Docker
make migrate        # Aplica migraciones
make runserver      # Levanta el server en localhost:8080
make migrations     # Genera nuevas migraciones
make shell          # Django shell
make lint           # black + isort + autoflake + flake8 (auto-fix)
make lint-check     # Solo verifica, no modifica
```

Sin Docker (requiere Postgres local):

```bash
source .venv/bin/activate
python manage.py runserver
python manage.py test
```

## Arquitectura en capas

Cada feature sigue el mismo flujo, de afuera hacia adentro:

```
Serializer (apps/api/v1/…)  →  DTO (pydantic BaseModel)  →  Service  →  Modelo Django (ORM)
```

- **Serializers** (`apps/api/v1/<recurso>/serializers.py`): validan la forma del request/response. No contienen lógica de negocio.
- **DTOs** (`apps/todos/dtos/`, `apps/users/dtos/`): objetos `pydantic.BaseModel` que representan "datos ya validados" pasando de la API a los servicios, desacoplados del modelo de Django.
- **Services** (`apps/todos/services/`, `apps/users/services/`): la lógica de negocio real (p. ej. `BoardService.create` crea el board *y* la membership de owner en una transacción).
- **Views** (`apps/api/v1/<recurso>/views.py`): orquestan permisos, querysets y delegan al serializer.

Ejemplo real — crear un board (`apps/api/v1/todos/serializers.py` → `apps/todos/services/board.py`):

```python
class BoardSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        data = BoardData(**validated_data)                       # DTO
        return BoardService.create(user=self.context["request"].user, data=data)  # Service
```

## Modelo de dominio

| Modelo | Relación | Rol |
|---|---|---|
| `User` (`apps/users/models.py`) | — | Autenticación por email, no username |
| `Profile` | 1:1 con `User` | Bio y avatar |
| `Board` (`apps/todos/models.py`) | pertenece a un `User` creador | Un tablero Kanban |
| `BoardMembership` | M:N entre `User` y `Board` (con `role`: `owner`/`member`) | Quién puede ver/editar cada board |
| `BoardStatus` | pertenece a un `Board` | Columnas del tablero (To Do, Doing, Done…) |
| `Sprint` | pertenece a un `Board` | Agrupa tasks por período |
| `Task` | pertenece a un `Board`, opcionalmente a un `Sprint`/`BoardStatus`, con `user` (creador) y `assigned_to` | La unidad de trabajo |
| `Comment` | pertenece a una `Task` | Comentarios de una task |
| `IdempotencyKey` | pertenece a un `User` | Dedupe de creaciones reintentadas (ver semana 12) |

## Autenticación y control de acceso

- **Login por email**, no username — `CustomTokenObtainPairSerializer` (`apps/api/v1/auth/serializers.py`).
- **JWT**: access token de 5 min, refresh de 1 día, con rotación y **blacklist** activada (`config/settings.py:SIMPLE_JWT`). `POST /api/v1/auth/logout/` invalida el refresh token del lado del servidor.
- **Ownership real**: ningún usuario ve boards/tasks/comments ajenos. El acceso se resuelve vía `BoardMembership` (`apps/api/v1/todos/permissions.py::boards_for_user`) — un recurso ajeno responde **404**, no 403, para no confirmar que existe (mitigación IDOR).
- **RBAC simple**: cualquier miembro (`owner` o `member`) puede operar sobre statuses/sprints/tasks/comments; solo el `owner` puede editar/borrar el board o gestionar miembros (`IsBoardOwnerForUnsafeMethods`).
- **Throttling**: `POST /api/v1/auth/token/` limitado a 5 intentos/min.
- **Password**: hasheado por Django; `PasswordComplexityValidator` (`apps/users/validators.py`) exige 12+ caracteres, mayúsculas/minúsculas y un carácter especial. `POST /api/v1/auth/password/validate/` permite validar antes de registrar.

## Endpoints principales

```
POST   /api/v1/auth/token/                     login (email + password)
POST   /api/v1/auth/token/refresh/
POST   /api/v1/auth/token/verify/
POST   /api/v1/auth/logout/                    invalida el refresh token
POST   /api/v1/auth/password/validate/

POST   /api/v1/users/register/
GET    /api/v1/users/

GET    /api/v1/boards/                         paginado, solo boards propios/compartidos
POST   /api/v1/boards/
GET    /api/v1/boards/{id}/
PATCH  /api/v1/boards/{id}/                    solo owner
DELETE /api/v1/boards/{id}/                    solo owner
GET    /api/v1/boards/{id}/members/
POST   /api/v1/boards/{id}/members/            invita por email, solo owner
DELETE /api/v1/boards/{id}/members/{id}/       solo owner

GET    /api/v1/boards/{id}/statuses/
GET    /api/v1/boards/{id}/sprints/
GET    /api/v1/boards/{id}/tasks/?status=&sprint=&assigned_to=   filtrable
POST   /api/v1/boards/{id}/tasks/              soporta header Idempotency-Key
GET    /api/v1/tasks/{id}/
GET    /api/v1/tasks/{id}/comments/
POST   /api/v1/tasks/{id}/comments/            soporta header Idempotency-Key
```

## Contrato para el equipo móvil (OpenAPI)

El schema se genera automáticamente con drf-spectacular y **no requiere mantenimiento manual**:

- `GET /api/schema/` — YAML/JSON descargable, es el contrato que le pasas al equipo móvil (o a un generador de clientes).
- `GET /api/docs/swagger/` — Swagger UI interactivo.
- `GET /api/docs/redoc/` — Redoc.

Se validó con `python manage.py spectacular --validate --fail-on-warn` sin errores ni warnings.

## Manejo de errores esperado por el cliente

| Código | Cuándo | Ejemplo |
|---|---|---|
| 401 | Token ausente/expirado/inválido | Falta el header `Authorization` |
| 403 | Autenticado pero sin permiso para la acción | Un `member` intenta borrar el board |
| 404 | Recurso inexistente **o** ajeno (no se revela cuál) | GET a un board del que no sos miembro |
| 400 | Validación de negocio | Asignar una task a alguien que no es miembro del board |
| 429 | Rate limit | Más de 5 intentos de login por minuto |

---

## Semana por semana: de la guía al código

| Semana | Tema clave de la guía | Cómo se aplica en este backend |
|---|---|---|
| **1-2** | Arquitectura cliente-servidor, patrones MVC/MVVM/Clean Architecture | Capas `Serializer → DTO → Service → Modelo` en `apps/todos/` y `apps/users/`: separa validación de entrada, transporte de datos y lógica de negocio, igual que MVVM separa vista/estado/dominio en el cliente. |
| **3** | Lenguajes, IDEs, gestores de paquetes | `requirements.txt` como gestor de dependencias del proyecto (equivalente a `package.json`/`pubspec.yaml` del lado móvil). |
| **4** | Arquitectura cliente-servidor, diseño de BD, Spec Driven Development | El modelo de datos (`apps/todos/models.py`) se diseñó antes de exponer endpoints. El schema OpenAPI (`/api/schema/`) es el "spec" formal que el equipo móvil puede consumir para generar código cliente. |
| **5** | Diseño de BD, normalización, ORMs | Modelo relacional normalizado: `Board`→`BoardStatus`/`Sprint`→`Task`→`Comment`, con `BoardMembership` como tabla asociativa M:N (patrón visto para relaciones muchos-a-muchos). Todo vía Django ORM, sin SQL crudo. |
| **6** | CRUD, diseño de endpoints REST, validación, respuestas JSON estandarizadas, checks de propiedad | Endpoints REST anidados por recurso (`boards/{id}/tasks/`), validación cruzada en `TaskSerializer.validate()` (sprint/status deben pertenecer al board), y ahora **todas** las vistas verifican ownership vía `BoardMembership` antes de responder. |
| **7** | JWT, RBAC, protección de rutas, hashing de contraseñas, OWASP API Top 10 (IDOR) | JWT con login por email y claims custom; `IsAuthenticated` global; `IsBoardOwnerForUnsafeMethods` como RBAC simple owner/member; el IDOR de boards/tasks visibles para cualquier usuario autenticado se corrigió filtrando por membership; contraseñas nunca en texto plano. |
| **8** | Caching, problema N+1, colas de background jobs, paginación, eficiencia en auth | Paginación (`PageNumberPagination`, 20/página) en todos los listados; `select_related` en Task y Comment para evitar N+1; JWT es stateless (no golpea sesión en cada request). **Pendiente**: no hay caching (Redis) ni cola de background jobs — no se necesitaron aún, pero quedan como próximo paso si el volumen lo justifica. |
| **9** | Entorno de desarrollo móvil, conectar la app al backend local, tráfico HTTP en desarrollo | `CORS_ALLOWED_ORIGINS` incluye `localhost:8081` y un placeholder de Expo (`exp://`) para que el emulador/dispositivo físico pueda pegarle al backend en desarrollo. |
| **10** | Sistemas de diseño UI, estados de componentes | No es responsabilidad del backend, pero se le da al front lo que necesita para pintar estado: `BoardStatus.color`, y timestamps `created`/`modified` para ordenar/mostrar actividad. |
| **11** | Navegación, manejo de estado, validación de formularios, diferenciar 401 de 403 | La API devuelve 401 (no autenticado) vs 403 (autenticado sin permiso) vs 404 (recurso ajeno) de forma consistente — la app móvil puede usar esto para decidir si redirige a login (401) o muestra "sin permiso" (403). |
| **12** | Persistencia local, almacenamiento seguro de tokens, sync offline, resolución de conflictos, patrón outbox con idempotencia, protección de datos (LOPDP) | `modified` (auto_now) en Board/Task/Comment sirve como timestamp autoritativo del servidor para resolución de conflictos "last-write-wins". Header `Idempotency-Key` en creación de tasks/comments soporta el patrón outbox (reintentar sin duplicar). El logout real (blacklist de refresh token) le da al cliente una forma de invalidar sesión del lado del servidor, no solo borrar el token local. |

### Gaps conocidos (no bloquean el desarrollo móvil, pero quedan anotados)

- Sin caching (Redis) ni cola de background jobs — semana 8.
- Registrar sin `first_name`/`last_name` todavía puede fallar (bug pre-existente en `apps/users/dtos/user.py`, fuera del alcance de esta ronda de cambios).
- No hay flujo de "olvidé mi contraseña".

Más detalle de la postura de seguridad en [docs/security.md](docs/security.md).
