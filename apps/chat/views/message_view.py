from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions, mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.chat.models import Message
from apps.chat.serializers import MessageSerializer
from apps.matches.models import Match


class MessageViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Esperamos recibir el match_id por URL o Query Param.
        Ejemplo: /api/chat/messages/?match_id=123
        """
        match_id = self.request.query_params.get("match_id")

        if not match_id:
            # Si no envían ID, no devolvemos nada (o podrías devolver error 400)
            return Message.objects.none()

        # 1. Verificar que el Match existe y que YO soy parte de él
        # Esto evita que alguien lea chats ajenos cambiando el ID
        try:
            match = Match.objects.get(id=match_id)
        except ObjectDoesNotExist:
            raise exceptions.NotFound("Match no encontrado") from None

        if self.request.user.profile not in match.user_a or match.user_b:
            raise exceptions.PermissionDenied("No tienes permiso para ver este chat.")

        # 2. Devolver mensajes ordenados (los más recientes primero para paginación inversa)
        return Message.objects.filter(match=match).order_by("-created_at")
