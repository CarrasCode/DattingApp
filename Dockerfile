FROM python:3.14-slim-bookworm

# 2. Copiamos 'uv' desde su imagen oficial (Best Practice)
# Esto es mucho más seguro y rápido que instalarlo con curl o pip
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 3. Variables de Entorno
# - PYTHONUNBUFFERED: Para ver los logs de Django en tiempo real
# - UV_COMPILE_BYTECODE: Hace que uv compile los .pyc al instalar (arranque más rápido)

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    # Esto asegura que cualquier comando 'python' o 'django-admin' use el entorno virtual
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

# 4. Instalación de dependencias del SISTEMA (GDAL/PostGIS)
# Esto es OBLIGATORIO para GeoDjango.
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    # Limpiamos caché para que la imagen pese menos
    && rm -rf /var/lib/apt/lists/*

# 5. Definimos el directorio de trabajo
WORKDIR /app


# 6. Copiamos SOLO los archivos de dependencias primero
# Esto permite aprovechar la caché de Docker. Si no cambias dependencias,
# Docker se salta este paso y la construcción es instantánea.
COPY pyproject.toml uv.lock ./

# 7. Instalamos las dependencias con uv
# --frozen: Usa exactamente las versiones del uv.lock (seguridad)
RUN uv sync --frozen

# 8. Copiamos el resto del código (apps, config, manage.py...)
COPY . .

# 9. Exponemos el puerto (informativo)
EXPOSE 8000

# Cuando esto corra en la nube, usará Gunicorn
CMD ["gunicorn", "DattingApp.wsgi:application", "--bind", "0.0.0.0:8000"]
