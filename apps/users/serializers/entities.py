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
