import uuid

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.gis.db import models as geomodels  # Importante para GeoDjango
from django.db import models
from django.db.models.functions import ExtractYear
from django.utils.translation import gettext_lazy as _

from .utils import calculate_age


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El email es obligatorio"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # Esto hashea la contraseña al usar AbstractBaseUser
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    # Configuración para usar email como login
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email


class ProfileManager(models.Manager):
    """
    Manager personalizado para agregar métodos de consulta
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
        Filtra perfiles por rango de edad.
        Método de conveniencia para queries comunes.
        """
        return self.with_age().filter(
            calculated_age__gte=min_age, calculated_age__lte=max_age
        )


class Profile(models.Model):
    class Gender(models.TextChoices):
        MALE = "M", _("Male")
        FEMALE = "F", _("Female")
        NON_BINARY = "NB", _("Non-Binary")
        OTHER = "O", _("Other")

    class GenderPreference(models.TextChoices):
        MEN = "M", _("Men")
        WOMEN = "F", _("Women")
        BOTH = "B", _("Both")
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

    @property
    def age(self):
        return calculate_age(self.birth_date)


class UserPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name="photos", related_name="photos"
    )
    image = models.ImageField(upload_to="user_photos/%Y/%m")
    caption = models.CharField(max_length=100, blank=True)

    # Importante: Saber cuál es la foto de perfil principal
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main", "-created"]  # La principal primero, luego las nuevas

    def __str__(self) -> str:
        return self.profile.first_name

    def save(self, *args, **kwargs):
        # Lógica extra: Si marco esta como main, desmarcar las otras
        if self.is_main:
            UserPhoto.objects.filter(profile=self.profile).update(is_main=False)
        super().save(*args, **kwargs)
