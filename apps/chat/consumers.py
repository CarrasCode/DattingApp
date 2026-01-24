import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1. Obtenemos el ID del match de la URL (ws/chat/<match_id>/)
        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        self.room_group_name = f"chat_{self.match_id}"

        # 2. Autenticación: ¿El usuario que se conecta pertenece a este Match?
        # (Esto es CRÍTICO para la privacidad, lo implementaremos en el paso de validación.
        # Por ahora asumimos que sí para probar la conexión básica).

        # 3. Unirse al grupo de Redis (La Sala)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # 4. Aceptar la conexión WebSocket
        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Recibir mensaje del WebSocket (del Frontend)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json["message"]
        user_id = self.scope[
            "user"
        ].id  # ID del usuario logueado (gracias al AuthMiddleware)

        # 1. Guardar mensaje en Base de Datos (Función auxiliar)
        # Necesitamos 'await' porque guardar en BD es una operación bloqueante
        await self.save_message(self.match_id, user_id, message_text)

        # 2. Enviar mensaje al grupo (Redis broadcast)
        # Esto hace que le llegue TAMBIÉN a la otra persona
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",  # Llama al método chat_message de abajo
                "message": message_text,
                "sender_id": user_id,
            },
        )

    # Este método se ejecuta cuando Redis nos avisa de un nuevo mensaje en el grupo
    async def chat_message(self, event):
        message = event["message"]
        sender_id = event["sender_id"]

        # Enviar al WebSocket (al Frontend)
        await self.send(
            text_data=json.dumps({"message": message, "sender_id": sender_id})
        )

    # --- Métodos Auxiliares para hablar con la Base de Datos ---
    # Como Django ORM es síncrono, necesitamos envolverlo en database_sync_to_async

    @database_sync_to_async
    def save_message(self, match_id, user_id, text):
        from apps.chat.models import Message
        from apps.social.models import Match

        match = Match.objects.get(id=match_id)
        # OJO: Asumimos que user.profile existe.
        # En producción deberías manejar excepciones.
        profile = self.scope["user"].profile

        return Message.objects.create(match=match, sender=profile, text=text)
