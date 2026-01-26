# ==========================================
# ETAPA 1: BUILDER
# Objetivo: Instalar herramientas pesadas para compilar dependencias,
# pero esta imagen se descartará al final.
# ==========================================
FROM python:3.14-slim-bookworm AS builder

# Traemos 'uv' directamente de su imagen oficial.
# Es más rápido y seguro que instalarlo manualmente con curl/pip.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Configuración para 'uv':
# UV_COMPILE_BYTECODE: Compila a .pyc ahora para que el arranque final sea veloz.
# UV_PROJECT_ENVIRONMENT: Define la ubicación fija del entorno virtual.
ENV UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /app

# Instalamos dependencias de SISTEMA para COMPILACIÓN.
# 'libgdal-dev' y 'build-essential' son pesados pero obligatorios
# [para construir las librerías de GeoDjango.
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    libgdal-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos solo los ficheros de requisitos para aprovechar la caché de Docker.
# Si no cambian estos archivos, Docker se salta el paso siguiente.
COPY pyproject.toml uv.lock ./

# Creamos el entorno virtual en /opt/venv.
# Las librerías se compilan usando las herramientas pesadas de arriba.
RUN uv sync --frozen

# ==========================================
# ETAPA 2: FINAL (Producción)
# Objetivo: Una imagen ligera que solo contiene lo necesario para ejecutar.
# ==========================================
FROM python:3.14-slim-bookworm

# PYTHONUNBUFFERED: Fuerza a que los logs salgan en tiempo real (vital para Docker).
# VIRTUAL_ENV: Activa el entorno virtual automáticamente para todos los comandos.
# PATH: Asegura que los ejecutables del venv tengan prioridad.
ENV PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Instalamos dependencias de SISTEMA para EJECUCIÓN (Runtime).
# Usamos 'gdal-bin' (librerías compartidas) en lugar de la versión '-dev'.
# Esto ahorra cientos de MB al no incluir cabeceras ni compiladores.
RUN apt-get update && apt-get install -y \
    binutils \
    gdal-bin \
    libgdal32 \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el entorno virtual YA PREPARADO desde la etapa 'builder'.
# Nos traemos las librerías de Python listas y dejamos atrás la "basura" de compilación.
COPY --from=builder /opt/venv /opt/venv

# Copiamos el código fuente de la aplicación.
COPY . .

EXPOSE 8000

# Ejecutamos Gunicorn vinculando al puerto 8000.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
