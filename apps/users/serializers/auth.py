from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers

from ..models import Profile

# El CustomUser de models
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password_confirm"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden."}
            )
        return attrs

    def create(self, validated_data):
        #  Elimina el campo de confirmación
        validated_data.pop("password_confirm")

        # IMPORTANTE: Al crear usuario, creamos su perfil vacío automáticamente
        # Esto es una buena práctica para evitar errores de "Profile not found" luego
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            Profile.objects.create(
                custom_user=user, first_name="", birth_date="2000-01-01"
            )

        return user
