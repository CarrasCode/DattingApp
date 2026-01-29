# Implementación: Configuración CORS y Corrección Auth

## Problema

1.  **CORS**: El Frontend (localhost:4200) no puede hablar con el Backend (localhost:8000) por seguridad del navegador. Necesitamos `django-cors-headers`.
2.  **Payload**: El servicio de Angular envía `{ credentials: { email, password } }` pero Django espera `{ email, password }`.

## User Review Required

> [!IMPORTANT]
> Se requiere regenerar `uv.lock` después de modificar `pyproject.toml`. Si `uv` no está instalado localmente, el build de Docker fallará.

## Proposed Changes

### Backend

#### [MODIFY] [pyproject.toml](file:///home/antonio/Documentos/DJango/DattingApp/backend/pyproject.toml)

- Añadir `django-cors-headers` a dependencias.

#### [MODIFY] [settings.py](file:///home/antonio/Documentos/DJango/DattingApp/backend/config/settings.py)

- `INSTALLED_APPS`: Añadir "corsheaders".
- `MIDDLEWARE`: Añadir "corsheaders.middleware.CorsMiddleware" (Arriba de CommonMiddleware). -`CORS_ALLOWED_ORIGINS`: Añadir "http://localhost:4200".

### Frontend

#### [MODIFY] [auth-service.ts](file:///home/antonio/Documentos/DJango/DattingApp/frontend/src/app/services/auth-service.ts)

- Enviar el objeto de credenciales directamente, sin anidar.

## Verification Plan

1.  **Backend**:
    - Ejecutar `uv lock` en local (o dentro del contenedor si no hay uv local).
    - Reconstruir Docker: `docker compose up --build`.
2.  **Frontend**:
    - Recargar la página.
    - Intentar Login.
    - Verificar en Network Tab que la petición es 200 OK y devuelve tokens.
