from typing import Any, override

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated

from ..filters import ProfileFilter
from ..models import Profile
from ..permissions import IsOwnerOrReadOnly
from ..serializers import (
    PrivateProfileSerializer,
    ProfileWriteSerializer,
    PublicProfileSerializer,
)
from ..services import annotate_distance_from_user, apply_matching_filters


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
    @override
    def get_queryset(self):  # type: ignore[override]
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

    @override
    def get_serializer_class(self):  # type: ignore[override]
        # 1. Escritura (Crear/Editar) -> Serializador de validación inputs
        if self.action in ["create", "update", "partial_update"]:
            return ProfileWriteSerializer

        # 2. Acción especial 'me' -> Serializador privado completo
        if self.action == "me":
            # Si es PUT o PATCH, usamos el de escritura para filtrar campos
            if self.request.method in ["PUT", "PATCH"]:
                return ProfileWriteSerializer
            return PrivateProfileSerializer

        # 3. Lectura general (Listar/Ver otros) -> Serializador público seguro
        return PublicProfileSerializer

    @override
    def get_object(self) -> Profile:  # type: ignore[override]
        """
        Sobrescribe get_object para manejar la acción 'me' de forma optimizada.

        - Para 'me': Query directa sin cálculos geoespaciales innecesarios
        - Para otras acciones: Usa el queryset estándar con todas las optimizaciones

        Returns:
            Profile: El perfil solicitado (propio o de otro usuario)

        Raises:
            NotFound: Si el usuario no tiene perfil creado (solo en acción 'me')
        """
        if self.action == "me":
            user = self.request.user

            try:
                # Query optimizada: solo carga lo necesario
                obj = (
                    Profile.objects.select_related("custom_user")
                    .prefetch_related("photos")
                    .get(custom_user=user)
                )
                # Validación manual de permisos a nivel de objeto
                # Esto ejecuta has_object_permission() de todos los permission_classes
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
