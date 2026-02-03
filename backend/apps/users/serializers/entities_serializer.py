from PIL import Image
from rest_framework import serializers

from ..models import UserPhoto


class UserPhotoSerializer(serializers.ModelSerializer):
    """
    Serializador para las fotos.
    Transforma el objeto ImageField en una URL completa.
    """

    class Meta:
        model = UserPhoto
        fields = ["id", "image", "is_main", "caption"]
        read_only_fields = ["id"]


class UserPhotoUploadSerializer(serializers.ModelSerializer):
    """
    Para SUBIR fotos (POST)
    Incluye validación de tamaño y formato.
    """

    MAX_SIZE_MB = 5
    MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024

    class Meta:
        model = UserPhoto
        fields = ["id", "image", "caption", "is_main"]
        read_only_fields = ["id"]

    def validate_image(self, value):
        # Validación extra: No dejar subir archivos según el tamaño
        if value.size > self.MAX_SIZE_BYTES:
            raise serializers.ValidationError(
                f"La imagen es demasiado pesada (>{self.MAX_SIZE_MB}MB)"
            )
        try:
            img = Image.open(value)
            img.verify()
        except Exception:
            raise serializers.ValidationError(
                "El archivo subido no es una imagen válida o está corrupto."
            ) from None
        return value
