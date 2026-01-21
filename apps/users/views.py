from typing import Any

from django.contrib.gis.db.models.functions import (
    Distance as DistanceFunc,
)  # Renombramos para no confundir
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, UserPhoto
from .permissions import HasProfile, IsOwnerOrReadOnly
from .serializers import (
    PrivateProfileSerializer,
    ProfileWriteSerializer,
    PublicProfileSerializer,
    UserPhotoSerializer,
    UserPhotoUploadSerializer,
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

        qs = (
            Profile.objects.select_related("custom_user")
            .prefetch_related("photos")
            .all()
        )
        # 2. Obtenemos la ubicación del usuario que hace la petición
        # OJO: Puede ser que el usuario nuevo aún no tenga ubicación (sea None)
        user: Any = self.request.user
        user_profile = user.profile
        if user_profile.location:
            # 3. Anotación Geoespacial
            # Calculamos la distancia desde 'location' (campo del perfil ajeno)
            # hasta 'user_profile.location' (mi ubicación).
            # El resultado se guarda en un atributo virtual llamado 'distance_obj'
            qs = qs.annotate(
                distance_obj=DistanceFunc("location", user_profile.location)
            )

            # (Opcional) Ordenar por cercanía
            qs = qs.order_by("distance_obj")

        return qs

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

    def get_object(self):
        """
        - Si la acción es 'me', devuelve el perfil del usuario logueado.
        - Si es otra acción (ej: /profiles/5/), usa la lógica normal (por ID).
        """
        if self.action == "me":
            queryset = self.get_queryset()
            user = self.request.user

            try:
                obj = queryset.get(custom_user=user)
                # IMPORTANTE: Check de permisos de objeto manual porque no pasamos por get_object normal
                self.check_object_permissions(self.request, obj)
                return obj
            except Profile.DoesNotExist:
                raise NotFound("No existe un perfil para este usuario.") from None

        return super().get_object()

    # --- ENDPOINT ESPECIAL: "ME" ---
    # URL: /api/users/profile/me/
    # Esto ahorra al frontend tener que guardar el ID del usuario.
    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        """
        Endpoint para obtener o editar el perfil del usuario actual.
        Delega la lógica a retrieve() o update() estándar.
        """
        # Delegamos a los mixins existentes. Código limpio.
        if request.method == "GET":
            return self.retrieve(request)
        return self.update(request)


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
