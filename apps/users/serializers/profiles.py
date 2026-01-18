from rest_framework import serializers

from ..models import Profile
from ..validators import validate_adult_age
from .entities import UserPhotoSerializer


class PublicProfileSerializer(serializers.ModelSerializer):
    """
    Datos seguros que cualquier usuario puede ver de otro.
    SIN email, SIN coordenadas exactas, SIN configuración.
    """

    age = serializers.ReadOnlyField()
    photos = UserPhotoSerializer(many=True, read_only=True)

    # No se envía las coordenadas del otro usuario al frontend.
    # Envías la "distancia calculada" (ej: "A 5 km").
    # Este campo lo calcularemos dinámicamente en la query (lo veremos luego).
    distance_km = serializers.IntegerField(read_only=True, required=False)

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
            "distance_km",  # Campo extra que vendrá anotado desde la base de datos
        ]


class PrivateProfileSerializer(PublicProfileSerializer):
    """
    Hereda del público y AÑADE los datos sensibles.
    """

    #  Mostrar el email del usuario (que está en otra tabla)
    email = serializers.CharField(source="custom_user.email", read_only=True)

    #  Formatear coordenadas (GeoDjango)
    # Convertimos el objeto Point a un array [lat, lng] fácil para Angular
    location = serializers.SerializerMethodField()

    class Meta(PublicProfileSerializer.Meta):
        # Tomamos los campos públicos y añadimos los privados
        fields = PublicProfileSerializer.Meta.fields + [
            "email",
            "birth_date",  # Yo sí necesito ver mi fecha para editarla
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
