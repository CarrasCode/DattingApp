from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Expresión regular para capturar el ID del match
    # Ejemplo: ws/chat/123/
    re_path(r"ws/chat/(?P<match_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]
