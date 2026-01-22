from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.matches.models.swipe import Swipe


class CurrentProfileDefault:
    """
    Clase para obtener el perfil del usuario actual desde el contexto.
    Es una solución para evitar sobreescribir el método create.
    """

    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["request"].user.profile

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class SwipeSerializer(serializers.ModelSerializer):
    # Usamos HiddenField para que el swiper no se pida en el JSON,
    # pero esté disponible para la creación y los validadores.
    swiper = serializers.HiddenField(default=CurrentProfileDefault())

    class Meta:
        model = Swipe
        fields = ["target", "value", "swiper"]
        validators = [
            UniqueTogetherValidator(
                queryset=Swipe.objects.all(),
                fields=["swiper", "target"],
                message="Ya has votado a este usuario anteriormente.",
            )
        ]

    def validate_target(self, value):
        """
        Validamos que el usuario no vote a su propio perfil.
        """
        # Obtenemos el perfil del contexto (ya validado por el default si se prefiere)
        request = self.context.get("request")
        if request and value == request.user.profile:
            raise serializers.ValidationError("No puedes darte like a ti mismo.")
        return value
