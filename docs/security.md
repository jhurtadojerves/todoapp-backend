# Seguridad: Control de acceso, credenciales y sesión

## Control de acceso

**Política global** — `config/settings.py`

```python
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework_simplejwt.authentication.JWTAuthentication"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.ScopedRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"login": "5/min"},
}
```

Todos los endpoints requieren autenticación JWT por defecto.

**Endpoints públicos** — declaran explícitamente `AllowAny`:

- `apps/api/v1/auth/views.py` — `PasswordValidationView`
- `apps/api/v1/users/views.py` — endpoint de registro

**Propiedad de recursos (ownership) — `apps/api/v1/todos/`**

Los boards ya no son de acceso global: cada `Board` tiene un conjunto de `BoardMembership` (owner/member) que determina quién puede verlo. Todas las vistas de boards, statuses, sprints, tasks y comments filtran su `get_queryset()` por membership del usuario autenticado (`apps/api/v1/todos/permissions.py::boards_for_user`), devolviendo 404 en vez de 403 para no confirmar la existencia de recursos ajenos (mitigación IDOR). Solo el owner de un board puede editarlo/eliminarlo o gestionar miembros (`IsBoardOwnerForUnsafeMethods`); cualquier miembro puede operar sobre statuses/sprints/tasks/comments del board.

**Idempotencia en creación** — `apps/api/v1/todos/idempotency.py`

`TaskListCreateView` y `CommentListCreateView` aceptan un header opcional `Idempotency-Key`. Si el cliente móvil reintenta una creación (por ejemplo tras perder conexión) con la misma clave, la API devuelve el recurso ya creado en vez de duplicarlo — pensado para el patrón outbox de sincronización offline.

---

## Almacenamiento de credenciales

**Hashing de contraseñas** — Django gestiona el hashing automáticamente via `AUTH_USER_MODEL = "users.User"` (`config/settings.py:198`). Las contraseñas nunca se almacenan en texto plano.

**Validación de complejidad** — `apps/users/validators.py`

- Mínimo 12 caracteres
- Mayúsculas + minúsculas
- Al menos un carácter especial

Registrado en `AUTH_PASSWORD_VALIDATORS` (`config/settings.py:108-127`).

**Generación de tokens** — `apps/api/v1/auth/serializers.py:12-40`

- `CustomTokenObtainPairSerializer`: login por **email** (no username)
- Añade claims `username` y `email` al JWT
- Firmado con `SECRET_KEY` via HS256

---

## Persistencia de sesión

**Configuración JWT** — `config/settings.py`

```python
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),   # corta vida
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),      # renovación diaria
    "ROTATE_REFRESH_TOKENS": True,                    # refresh rota en cada uso
    "BLACKLIST_AFTER_ROTATION": True,                 # el refresh usado queda invalidado
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
}
```

`rest_framework_simplejwt.token_blacklist` está registrado en `INSTALLED_APPS`, lo que agrega las tablas `OutstandingToken`/`BlacklistedToken`.

**Endpoints de gestión de sesión** — `apps/api/v1/auth/views.py`

| View | Ruta | Función |
|---|---|---|
| `TokenCreateView` | `POST /api/v1/auth/token/` | Login, emite access + refresh (throttled: 5/min) |
| `TokenRefreshView` | `POST /api/v1/auth/token/refresh/` | Renueva el access token (rota el refresh) |
| `TokenVerifyView` | `POST /api/v1/auth/token/verify/` | Valida si un token es vigente |
| `LogoutView` | `POST /api/v1/auth/logout/` | Recibe el refresh token y lo agrega a la blacklist |

**Logout real:** el cliente móvil debe llamar a `POST /api/v1/auth/logout/` con `{"refresh": "<token>"}` al cerrar sesión. Esto invalida el refresh token del lado del servidor (no solo se borra localmente). Los access tokens siguen expirando solos a los 5 minutos y no se pueden revocar individualmente antes de su expiración — es una limitación aceptada dado su corto tiempo de vida.
