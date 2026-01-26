"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from apps.chat.middleware import JWTAuthMiddleware
from apps.chat.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Inicializamos la app django normal primero
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # 1. Tráfico HTTP normal (vistas, API, admin)
        "http": django_asgi_app,
        # 2. Tráfico WebSocket (Chat, Notificaciones)
        "websocket": JWTAuthMiddleware(  # Autentica con JWT desde query param ?token=xxx
            URLRouter(websocket_urlpatterns)
        ),
    }
)
