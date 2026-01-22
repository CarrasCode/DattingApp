from rest_framework import serializers

from ..models import Profile
from ..validators import validate_adult_age
from .entities_serializer import UserPhotoSerializer


class BaseProfileSerializer(serializers.ModelSerializer):
    """
    Clase Base de Perfil, hecho para heredar
    """

    age = serializers.ReadOnlyField()
    photos = UserPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "bio",
            "work",
            "age",
            "gender",
            "photos",
        ]


class PublicProfileSerializer(BaseProfileSerializer):
    """
    Datos seguros que cualquier usuario puede ver de otro.
    SIN email, SIN coordenadas exactas, SIN configuración.
    """

    # No se envía las coordenadas del otro usuario al frontend.
    # Envías la "distancia calculada" (ej: "A 5 km").
    # Este campo lo calcularemos dinámicamente en la query (lo veremos luego).
    distance_km = serializers.SerializerMethodField()

    class Meta(BaseProfileSerializer.Meta):
        fields = BaseProfileSerializer.Meta.fields + [
            "distance_km",
        ]

    def get_distance_km(self, obj):
        """
        Este método se ejecuta por cada perfil para extraer el valor.
        """
        # 1. Verificamos si la vista hizo la anotación (annotate)
        # Si el usuario no tiene ubicación, 'distance_obj' no existirá.
        if not hasattr(obj, "distance_obj") or obj.distance_obj is None:
            return None

        # 2. GeoDjango devuelve un objeto Distance.
        # Podemos acceder a .km, .m, .mi (millas), etc.
        return int(obj.distance_obj.km)  # Convertimos a entero (5.4 km -> 5 km)


class PrivateProfileSerializer(BaseProfileSerializer):
    """
    AÑADE los datos sensibles.
    """

    #  Mostrar el email del usuario (que está en otra tabla)
    email = serializers.CharField(source="custom_user.email", read_only=True)

    #  Formatear coordenadas (GeoDjango)
    # Convertimos el objeto Point a un array [lat, lng] fácil para Angular
    location = serializers.SerializerMethodField()

    class Meta(BaseProfileSerializer.Meta):
        fields = BaseProfileSerializer.Meta.fields + [
            "email",
            "birth_date",
            "gender_preference",
            "max_distance",
            "min_age",
            "max_age",
            "location",
        ]

    def get_location(self, obj):
        if obj.location:
            return {"lat": obj.location.y, "lng": obj.location.x}
        return None


class ProfileWriteSerializer(serializers.ModelSerializer):
    """
    Serializador DE ESCRITURA.
    Valida los datos de entrada para actualizar el perfil.
    """

    birth_date = serializers.DateField(validators=[validate_adult_age])

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "bio",
            "work",
            "birth_date",
            "gender",
            "gender_preference",
            "max_distance",
            # Nota: Location se suele actualizar en un endpoint aparte
        ]
