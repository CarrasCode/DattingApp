import os
import uuid
from dataclasses import dataclass
from io import BytesIO

from django.core.files.base import ContentFile
from django.db import models, transaction
from PIL import Image

from .profiles import Profile


@dataclass(frozen=True)
class ImageConfig:
    format: str = "JPEG"
    extension: str = ".jpg"
    quality: int = 85
    max_dimension: int = 480


IMAGE_SETTINGS = ImageConfig()


def get_file_path(instance, filename: str) -> str:
    """
    Generar nombres únicos: "user_id/photos/uuid-generado.jpg"
    Cambiando el nombre de la extension siempre a jpg
    """
    filename = f"{uuid.uuid4()}{IMAGE_SETTINGS.extension}"
    return os.path.join(f"user_{instance.profile.id}", "photos", filename)


class UserPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        verbose_name="photos",
        related_name="photos",
    )
    image = models.ImageField(upload_to=get_file_path)
    caption = models.CharField(max_length=100, blank=True)

    # Importante: Saber cuál es la foto de perfil principal
    is_main = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

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
        if not self.image:
            return

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
            img.height > IMAGE_SETTINGS.max_dimension
            or img.width > IMAGE_SETTINGS.max_dimension
        ):
            output_size = (
                IMAGE_SETTINGS.max_dimension,
                IMAGE_SETTINGS.max_dimension,
            )
            img.thumbnail(output_size, Image.Resampling.LANCZOS)

        # 4. Guardar archivo final
        # Guardamos SIEMPRE para unificar formato  y calidad

        # Creas el "archivo virtual" vacío en la memoria RAM
        output_io = BytesIO()

        # Pillow escribe los 0s y 1s del formato JPEG dentro de esa variable en RAM.
        img.save(
            output_io,
            format=IMAGE_SETTINGS.format,
            quality=IMAGE_SETTINGS.quality,
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
