from typing import Any

from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    PrivateProfileSerializer,
    ProfileWriteSerializer,
    PublicProfileSerializer,
    UserRegistrationSerializer,
)


# --- 1. VISTA DE REGISTRO (CreateAPIView) ---
# Usamos CreateAPIView porque solo queremos una acción: POST.
# No necesitamos listar usuarios ni borrarlos aquí.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Importante: El registro debe ser público


class LogoutView(APIView):
    """
    Vista para cerrar sesión.
    Recibe el 'refresh_token' y lo pone en la lista negra para que no pueda volver a usarse.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            raise ValidationError({"detail": "El campo 'refresh' es obligatorio."})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            raise ValidationError({"detail": "Token inválido o expirado."}) from None


# --- 2. VIEWSET DE PERFILES (ModelViewSet) ---
# Usamos GenericViewSet + los Mixins específicos que SI queremos.
# Quitamos CreateModelMixin y DestroyModelMixin.
class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # --- OPTIMIZACIÓN DE BD ---
    def get_queryset(self) -> Any:
        """
        Aquí resolvemos el problema N+1.
        Si tienes 20 perfiles y cada uno tiene fotos y usuario,
        Django haría 1 query principal + 20 por usuarios + 20 por fotos = 41 queries.

        Con select_related y prefetch_related, Django hace JOINS inteligentes
        y lo reduce a solo 2 queries.
        """
        return (
            Profile.objects.select_related("custom_user")
            .prefetch_related("photos")
            .all()
        )

    # --- SERIALIZADOR DINÁMICO ---
    def get_serializer_class(self) -> Any:
        # 1. Escritura (Crear/Editar) -> Serializador de validación inputs
        if self.action in ["create", "update", "partial_update"]:
            return ProfileWriteSerializer

        # 2. Acción especial 'me' -> Serializador privado completo
        if self.action == "me":
            return PrivateProfileSerializer

        # 3. Lectura general (Listar/Ver otros) -> Serializador público seguro
        return PublicProfileSerializer

    # --- ENDPOINT ESPECIAL: "ME" ---
    # URL: /api/users/profile/me/
    # Esto ahorra al frontend tener que guardar el ID del usuario.
    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        """
        Endpoint para obtener o editar el perfil del usuario actual.
        Delega la lógica a retrieve() o update() estándar.
        """
        # Obtenemos el perfil del usuario logueado
        # Usamos get_queryset para mantener las optimizaciones (prefetch_related)
        # 1. Obtener el objeto del usuario actual
        try:
            profile = self.get_queryset().get(custom_user=request.user)
        except Profile.DoesNotExist:
            raise NotFound(
                "No se encontró un perfil asociado a este usuario."
            ) from None

        # 2. Si es GET, actuamos como si fuera un 'retrieve' normal
        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data)

        # 3. Si es PUT/PATCH, actuamos como un 'update' normal
        elif request.method in ["PUT", "PATCH"]:
            # Forzamos partial=True si es PATCH
            partial = request.method == "PATCH"
            serializer = self.get_serializer(
                profile, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Re-serializamos con el Private para devolver la respuesta bonita y actualizada
            response_serializer = PrivateProfileSerializer(profile)
            return Response(response_serializer.data)
