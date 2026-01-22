from typing import cast

from django.contrib.gis.db.models.functions import Distance as DistanceFunc
from django.db.models import QuerySet

from ..models import Profile, ProfileQuerySet


def apply_matching_filters(
    queryset: QuerySet[Profile],
    user_profile: Profile,
    exclude_user_id: int | None = None,
) -> QuerySet[Profile]:
    """
    Aplica los filtros de matching según las preferencias del usuario.

    Args:
        queryset: QuerySet base de perfiles
        user_profile: Perfil del usuario que está filtrando
        exclude_user_id: ID del usuario a excluir (usualmente el propio)

    Returns:
        QuerySet filtrado según preferencias
    """
    # 1. Excluir al usuario actual
    if exclude_user_id:
        queryset = queryset.exclude(custom_user_id=exclude_user_id)

    # 2. Filtro de género
    if user_profile.gender_preference and user_profile.gender_preference != "A":
        queryset = queryset.filter(gender=user_profile.gender_preference)

    # 3. Filtro de edad
    queryset = cast(ProfileQuerySet, queryset).in_age_range(
        user_profile.min_age, user_profile.max_age
    )

    # 4. Filtro de distancia
    if user_profile.location and user_profile.max_distance:
        max_meters = user_profile.max_distance * 1000
        queryset = queryset.filter(distance_obj__lte=max_meters)

    return queryset


def annotate_distance_from_user(
    queryset: QuerySet[Profile], user_profile: Profile
) -> QuerySet[Profile]:
    """
    Anota la distancia de cada perfil respecto al usuario.

    Args:
        queryset: QuerySet de perfiles
        user_profile: Perfil del usuario de referencia

    Returns:
        QuerySet con anotación 'distance_obj' y ordenado por distancia
    """
    if not user_profile.location:
        return queryset

    return queryset.annotate(
        distance_obj=DistanceFunc("location", user_profile.location)
    ).order_by("distance_obj")
