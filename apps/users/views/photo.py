from typing import Any

from rest_framework import viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from ..models import UserPhoto
from ..permissions import HasProfile, IsOwnerOrReadOnly
from ..serializers import (
    UserPhotoSerializer,
    UserPhotoUploadSerializer,
)


class UserPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, HasProfile]
    # Estos parsers son OBLIGATORIOS para subir archivos
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self) -> Any:
        # Solo mis fotos
        return UserPhoto.objects.filter(profile__custom_user=self.request.user)

    def get_serializer_class(self) -> Any:
        if self.action == "create":
            return UserPhotoUploadSerializer
        return UserPhotoSerializer

    def perform_create(self, serializer):
        user: Any = self.request.user
        # Al guardar, inyectamos el perfil del usuario automáticamente
        # para que no tenga que enviarlo en el form-data

        serializer.save(profile=user.profile)
