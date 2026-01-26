import uuid
from datetime import date

from django.contrib.gis.db import models as geomodels  # Importante para GeoDjango
from django.db import models
from django.db.models.functions import ExtractYear
from django.utils.translation import gettext_lazy as _

from ..utils import calculate_age
from .users import CustomUser


class ProfileQuerySet(models.QuerySet):
    """
    QuerySet personalizado para agregar métodos de consulta
    relacionados con la edad
    """

    def with_age(self):
        """
        Anota la edad calculada usando AGE() para poder filtrar por ella.
        """
        return self.annotate(
            calculated_age=ExtractYear(
                models.Func(models.F("birth_date"), function="AGE")
            )
        )

    def in_age_range(self, min_age, max_age):
        """
        Filtra perfiles por rango de edad calculando el rango de fechas de nacimiento.
        Evita usar AGE() en el WHERE para mejorar performance y compatibilidad.
        """
        today = date.today()

        # Fecha máxima de nacimiento para tener al menos min_age años
        try:
            latest_birth_date = today.replace(year=today.year - min_age)
        except ValueError:
            # En caso de bisiesto (29 feb) y año no bisiesto, usamos 28 feb
            latest_birth_date = today.replace(year=today.year - min_age, day=28)

        # Fecha mínima de nacimiento para tener como máximo max_age años
        # (Es decir, ser menor de max_age + 1)
        try:
            earliest_birth_date_limit = today.replace(year=today.year - (max_age + 1))
        except ValueError:
            earliest_birth_date_limit = today.replace(
                year=today.year - (max_age + 1), day=28
            )

        # Filtro:
        # birth_date <= latest_birth_date  => Ya cumplió min_age
        # birth_date > earliest_birth_date_limit => No ha cumplido max_age + 1
        return self.filter(
            birth_date__lte=latest_birth_date, birth_date__gt=earliest_birth_date_limit
        )


class ProfileManager(models.Manager.from_queryset(ProfileQuerySet)):
    """
    Manager que hereda los métodos del QuerySet personalizado.
    Esto ayuda a que herramientas de análisis estático (como Pylance)
    detecten los métodos correctamente.
    """

    pass


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        NON_BINARY = "NB", _("Non-Binary")
        OTHER = "O", _("Other")

    class GenderPreference(models.TextChoices):
        MEN = "M", _("Men")
        WOMEN = "F", _("Women")
        ALL = "A", _("All")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=50)
    bio = models.TextField(max_length=1000, blank=True)
    birth_date = models.DateField()

    gender = models.CharField(max_length=2, choices=Gender.choices)
    gender_preference = models.CharField(
        max_length=1, choices=GenderPreference.choices, default=GenderPreference.ALL
    )

    work = models.CharField(max_length=50, blank=True)

    # srid=4326 es el estándar GPS (latitud/longitud)
    location = geomodels.PointField(srid=4326, null=True, blank=True)

    max_distance = models.IntegerField(default=50, help_text=_("Distancia en KM"))
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=99)

    objects = ProfileManager()

    def __str__(self) -> str:
        return f"{self.first_name} - {self.custom_user.email}"

    # Estandarización: Creamos un alias 'owner'
    @property
    def owner(self):
        return self.custom_user

    @property
    def age(self):
        return calculate_age(self.birth_date)
