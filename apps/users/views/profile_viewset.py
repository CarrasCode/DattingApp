from typing import Any

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from services import annotate_distance_from_user, apply_matching_filters

from ..filters import ProfileFilter
from ..models import Profile
from ..permissions import IsOwnerOrReadOnly
from ..serializers import (
    PrivateProfileSerializer,
    ProfileWriteSerializer,
    PublicProfileSerializer,
)


# --- VIEWSET DE PERFILES (ModelViewSet) ---
# Usamos GenericViewSet + los Mixins específicos que SI queremos.
# Quitamos CreateModelMixin y DestroyModelMixin.
class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_class = ProfileFilter

    # --- OPTIMIZACIÓN DE BD ---
    def get_queryset(self) -> Any:
        """
        Aquí resolvemos el problema N+1.
        Si tienes 20 perfiles y cada uno tiene fotos y usuario,
        Django haría 1 query principal + 20 por usuarios + 20 por fotos = 41 queries.

        Con select_related y prefetch_related, Django hace JOINS inteligentes
        y lo reduce a solo 2 queries.
        """
        # 1. PREPARACIÓN DE LA QUERY
        # - optimizaciones: Carga tablas relacionadas para no hacer 100 queries.
        qs = Profile.objects.select_related("custom_user").prefetch_related("photos")

        # Obtenemos el perfil del usuario logueado (nuestras "Settings")
        user: Any = self.request.user
        user_profile = user.profile

        # 2. LÓGICA GEOESPACIAL (Distancia)
        qs = annotate_distance_from_user(qs, user_profile)

        # 3. FILTRADO ESTRICTO (Solo en el listado / Feed)
        if self.action == "list":
            qs = apply_matching_filters(
                queryset=qs,
                user_profile=user_profile,
                exclude_user_id=user.id,
            )
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

        return self.update(request, partial=request.method == "PATCH")
