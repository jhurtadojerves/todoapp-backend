# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Docker-based (primary workflow)

```bash
make build          # Build Docker images
make runserver      # Run dev server at localhost:8080
make migrate        # Apply migrations
make migrations     # Generate new migrations
make shell          # Open Django shell
```

### Linting

```bash
make lint           # Auto-fix: black, isort, autoflake, then flake8
make lint-check     # Check only (no changes): black, isort, flake8
```

### Running tests

```bash
docker compose run --rm app python manage.py test
docker compose run --rm app python manage.py test apps.users  # single app
```

### Without Docker (requires local PostgreSQL)

```bash
source .venv/bin/activate
python manage.py runserver
python manage.py test
```

## Architecture

**Django 6 REST API** with PostgreSQL, JWT authentication, and OpenAPI docs.

### App layout

- [config/](config/) — Django settings, root URLconf, WSGI/ASGI
- [apps/users/](apps/users/) — Custom `User` model (email as `USERNAME_FIELD`), `Profile` model, domain logic
- [apps/api/](apps/api/) — API layer, versioned under `v1/`

### URL structure

```
/api/v1/auth/   → apps.api.v1.auth  (JWT tokens, password validation)
/api/v1/users/  → apps.api.v1.users (registration, user list)
/api/schema/    → OpenAPI schema (drf-spectacular)
/api/docs/swagger/
/api/docs/redoc/
```

### Layered architecture inside `apps/users/`

```
serializers (apps/api/v1/) → DTOs (pydantic BaseModel) → Services → Django ORM models
```

- **DTOs** (`apps/users/dtos/`): Pydantic `BaseModel` classes (`UserData`, `ProfileData`) used to pass validated data between the API layer and services.
- **Services** (`apps/users/services/`): Business logic. `UserService.register()` creates a `User` + `Profile` atomically. `ProfileService` handles profile creation.
- **Serializers** (`apps/api/v1/users/serializers.py`, `apps/api/v1/auth/serializers.py`): DRF serializers handle input validation and call into services/DTOs.

### Auth

- JWT via `djangorestframework-simplejwt`. Login is by **email** (not username). Tokens include `username` and `email` claims.
- `CustomTokenObtainPairSerializer` overrides the standard serializer to accept email instead of username.
- Default: access token 5 min, refresh token 1 day.
- All endpoints require `IsAuthenticated` by default; public endpoints set `permission_classes = [AllowAny]` explicitly.

### Password validation

`PasswordComplexityValidator` (registered in `AUTH_PASSWORD_VALIDATORS`) enforces: min 12 chars, mixed case, at least one special character. The `/api/v1/auth/password-validate/` endpoint allows pre-flight password checks without registration.

### Adding a new API endpoint

1. Add model to `apps/users/models.py` (or a new Django app)
2. Create DTO in `apps/users/dtos/`
3. Create service in `apps/users/services/`
4. Create serializer in `apps/api/v1/<resource>/serializers.py`
5. Create view in `apps/api/v1/<resource>/views.py` — decorate with `@extend_schema(tags=["v1/<resource>"])`
6. Wire URL in `apps/api/v1/<resource>/urls.py` and include in `apps/api/v1/urls.py`
7. Register the tag in `SPECTACULAR_SETTINGS["TAGS"]` in [config/settings.py](config/settings.py)
