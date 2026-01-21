from django_filters import BooleanFilter, FilterSet

from .models import Profile


class ProfileFilter(FilterSet):
    # Solo filtramos cosas "extra" que no sean preferencias guardadas,
    # por ejemplo, filtrar por si tienen foto o biografía.

    has_bio = BooleanFilter(field_name="bio", lookup_expr="isnull", exclude=True)

    class Meta:
        model = Profile
        fields = ["has_bio"]
