from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # Expresión regular para capturar el UUID del match
    # Ejemplo: ws/chat/123/
    re_path(r"ws/chat/(?P<match_id>[0-9a-f-]+)/$", consumers.ChatConsumer.as_asgi()),
]
