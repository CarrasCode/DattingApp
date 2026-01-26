import json
from typing import Any

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            # Rechazar la conexión si el usuario no está autenticado
            await self.close(code=4003)
            return

        # 1. Obtenemos el ID del match de la URL (ws/chat/<match_id>/)
        try:
            self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        except KeyError:
            await self.close(code=4000)
            return

        self.room_group_name = f"chat_{self.match_id}"

        # 2. Autenticación: ¿El usuario que se conecta pertenece a este Match?
        # (Esto es CRÍTICO para la privacidad, lo implementaremos en el paso de validación.
        # Por ahora asumimos que sí para probar la conexión básica).

        is_member = await self.check_match_permissions(self.match_id, self.user)
        if not is_member:
            await self.close(code=4003)  # Forbidden
            return

        # 3. Unirse al grupo de Redis (La Sala)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 4. Aceptar la conexión WebSocket
        await self.accept()

    async def disconnect(self, code):
        # Salir del grupo
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Recibir mensaje del WebSocket (del Frontend)
    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return

        # Parseo seguro del JSON
        try:
            text_data_json = json.loads(text_data)
            message_text = text_data_json["message"]
        except json.JSONDecodeError:
            await self.send_error("Invalid JSON format.")
            return

        if not message_text or not isinstance(message_text, str):
            await self.send_error("Message cannot be empty")
            return

        # Limpiar espacios (opcional pero recomendado)
        message_text = message_text.strip()
        if not message_text:
            return

        user_id = self.scope.get("user").id
        # ID del usuario logueado (gracias al AuthMiddleware)

        # 1. Guardar mensaje en Base de Datos (Función auxiliar)
        # Necesitamos 'await' porque guardar en BD es una operación bloqueante
        saved_message = await self.save_message(self.match_id, user_id, message_text)

        if not saved_message:
            await self.send_error("Failed to save message.")
            return

        # 2. Enviar mensaje al grupo (Redis broadcast)
        # Esto hace que le llegue TAMBIÉN a la otra persona
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # Llama al método chat_message de abajo
                "message": message_text,
                "sender_id": user_id,
                "timestamp": str(saved_message.created_at),
            },
        )

    # Este método se ejecuta cuando Redis nos avisa de un nuevo mensaje en el grupo
    async def chat_message(self, event: dict[str, Any]):
        # Manejador del broadcast para enviar al socket
        await self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "sender_id": event["sender_id"],
                    "timestamp": event.get("timestamp"),
                }
            )
        )

    async def send_error(self, error_message: str):
        """Helper para enviar errores estandarizados al frontend"""
        await self.send(text_data=json.dumps({"error": error_message}))

    # --- Métodos Auxiliares para hablar con la Base de Datos ---
    # Como Django ORM es síncrono, necesitamos envolverlo en database_sync_to_async

    @database_sync_to_async
    def save_message(self, match_id, user_id, text):
        from apps.chat.models import Message
        from apps.matches.models import Match

        try:
            match = Match.objects.get(id=match_id)
            profile = self.user.profile

            return Message.objects.create(match=match, sender=profile, text=text)

        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def check_match_permissions(self, match_id, user) -> bool:
        from apps.matches.models import Match

        # Verificamos existencia Y pertenencia en una sola query
        try:
            match = Match.objects.get(id=match_id)
            # Validar si el usuario es parte del match
            return match.user_a == user.profile or match.user_b == user.profile

        except ObjectDoesNotExist:
            return False
