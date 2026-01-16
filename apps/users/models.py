import uuid
from datetime import date

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("El email es obligatorio"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
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
        Anota la edad calculada para poder filtrar por ella.
        """
        today = date.today()
        return self.annotate(
            calculated_age=models.ExpressionWrapper(
                today.year - models.F("birth_date__year"),
                output_field=models.IntegerField(),
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
    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("NB", "Non-Binary"),
        ("O", "Other"),
    ]
    PREFERENCE_CHOICES = [
        ("M", "Men"),
        ("F", "Women"),
        ("B", "Both"),
        ("A", "All"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    first_name = models.CharField(max_length=50)
    bio = models.TextField(max_length=1000, blank=True)
    birth_date = models.DateField()
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    gender_preference = models.CharField(
        max_length=1, choices=PREFERENCE_CHOICES, default="A"
    )
    work = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100)
    max_distance = models.IntegerField(default=50)
    min_age = models.IntegerField(default=18)
    max_age = models.IntegerField(default=99)

    objects = ProfileManager()

    def __str__(self) -> str:
        return f"{self.first_name} - {self.custom_user.email}"

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.birth_date.year
            - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        )


class UserPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    custom_user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, verbose_name="photos"
    )
    image = models.ImageField(upload_to="user_photos/%Y/%m")
    caption = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]

    def __str__(self) -> str:
        return self.custom_user.email
