import os
import uuid
from io import BytesIO

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.gis.db import models as geomodels  # Importante para GeoDjango
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.db.models.functions import ExtractYear
from django.utils.translation import gettext_lazy as _
from PIL import Image

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

    # Estandarización: Creamos un alias 'owner'
    @property
    def owner(self):
        return self.custom_user

    @property
    def age(self):
        return calculate_age(self.birth_date)


IMAGE_SETTINGS = {
    "format": "JPEG",
    "extension": ".jpg",
    "quality": 85,
    "max_dimension": 1080,
}


def get_file_path(instance, filename: str) -> str:
    """
    Generar nombres únicos: "user_id/photos/uuid-generado.jpg"
    Cambiando el nombre de la extension siempre a jpg
    """
    filename = f"{uuid.uuid4()}{IMAGE_SETTINGS['extension']}"
    return os.path.join(f"user_{instance.profile.id}", "photos", filename)


class UserPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name="photos", related_name="photos"
    )
    image = models.ImageField(upload_to=get_file_path)
    caption = models.CharField(max_length=100, blank=True)

    # Importante: Saber cuál es la foto de perfil principal
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-is_main", "-created"]  # La principal primero, luego las nuevas

    def __str__(self) -> str:
        return f"Photo ({self.id}) - {self.profile.first_name}"

    def save(self, *args, **kwargs):
        """
        Sobreescribimos save para asegurar integridad en 'is_main'
        y procesar la imagen automáticamente.
        """

        with transaction.atomic():
            # Lógica extra: Si marco esta como main, desmarcar las otras
            if self.is_main:
                UserPhoto.objects.filter(profile=self.profile).update(is_main=False)

            # Solo procesar si la imagen es nueva o ha cambiado (no está committeada al storage)
            if self.image and not getattr(self.image, "_committed", False):
                self.process_image()

            super().save(*args, **kwargs)

    def process_image(self):
        """
        Normaliza la imagen: Corrige rotación, convierte a RGB,
        redimensiona y comprime a JPEG.
        """
        img = Image.open(self.image)

        # Corregir orientación EXIF (común en fotos de móvil)
        try:
            from PIL import ImageOps

            # exif_transpose devuelve una copia si la rota, o la misma img si no
            fixed_img = ImageOps.exif_transpose(img)
            if fixed_img is not img:
                img = fixed_img
        except Exception:
            # Si los datos EXIF están corruptos, ignoramos el error y
            # seguimos con la imagen original para no bloquear la subida.
            pass

        # 2. Convertir a RGB (Standard para web/jpg)
        if img.mode != "RGB":
            # Si es PNG con transparencia (RGBA), poner fondo blanco
            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert("RGB")

        # 3. Redimensionar (solo si es muy grande)
        if (
            img.height > IMAGE_SETTINGS["max_dimension"]
            or img.width > IMAGE_SETTINGS["max_dimension"]
        ):
            output_size = (
                IMAGE_SETTINGS["max_dimension"],
                IMAGE_SETTINGS["max_dimension"],
            )
            img.thumbnail(output_size, Image.Resampling.LANCZOS)

        # 4. Guardar archivo final
        # Guardamos SIEMPRE para unificar formato  y calidad

        # Creas el "archivo virtual" vacío en la memoria RAM
        output_io = BytesIO()

        # Pillow escribe los 0s y 1s del formato JPEG dentro de esa variable en RAM.
        img.save(
            output_io,
            format=IMAGE_SETTINGS["format"],
            quality=IMAGE_SETTINGS["quality"],
            optimize=True,
        )
        # .getvalue() extrae todo el contenido crudo (los bytes reales) de ese archivo virtual.
        # ContentFile coge esos bytes y los empaqueta para que Django los entienda como un archivo subido.
        new_image = ContentFile(output_io.getvalue())

        # Guardamos en el campo. save=False evita bucle infinito de save() del modelo
        self.image.save(self.image.name, new_image, save=False)

    # Estandarización: Creamos un alias 'owner'
    @property
    def owner(self):
        return self.profile.custom_user
