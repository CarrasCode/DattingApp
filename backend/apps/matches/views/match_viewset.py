from typing import Any

from django.contrib.gis.db.models.functions import Distance
from django.db.models import Case, F, Q, When
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.matches.models import Match
from apps.matches.serializers import MatchSerializer
from apps.users.permissions import HasProfile


class MatchViewSet(viewsets.ReadOnlyModelViewSet, mixins.DestroyModelMixin):
    """
    ViewSet de solo lectura y eliminación para los Matches.
    Permite listar y obtener detalles de los matches del usuario autenticado.
    """

    serializer_class = MatchSerializer
    permission_classes = [IsAuthenticated, HasProfile]

    def get_queryset(self):
        """
        Retorna los matches del usuario autenticado, ya sea que figure
        como user_a o user_b.
        """

        user: Any = self.request.user
        profile = user.profile

        qs = (
            Match.objects.filter(Q(user_a=profile) | Q(user_b=profile), is_active=True)
            .select_related("user_a__custom_user", "user_b__custom_user")
            .order_by("-created_at")
        )
        # 2. Lógica Geoespacial :
        # Si el usuario tiene ubicación, calculamos la distancia en la DB.
        if profile.location:
            qs = (
                qs.annotate(
                    # Determinamos dinámicamente la ubicación del "otro"
                    other_location=Case(
                        When(user_a=profile, then=F("user_b__location")),
                        default=F("user_a__location"),
                    )
                )
                .annotate(
                    # Calculamos distancia entre MI ubicación y la del "otro"
                    distance_val=Distance("other_location", profile.location)
                )
                .order_by("distance_val", "-created_at")
            )  # Opcional: ordenar por cercanía

        return qs
