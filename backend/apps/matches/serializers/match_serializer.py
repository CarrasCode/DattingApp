from rest_framework import serializers

from apps.users.serializers import PublicProfileSerializer

from ..models import Match


class MatchSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()
    # Mapeamos el valor anotado en la View.
    # Usamos un valor por defecto por si el usuario no tiene ubicación.
    distance = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ["id", "created_at", "other_user", "distance"]

    def get_other_user(self, obj):
        request = self.context.get("request")
        if not request:
            return None

        current_profile = request.user.profile
        target = obj.user_b if obj.user_a == current_profile else obj.user_a
        return PublicProfileSerializer(target, context=self.context).data

    def get_distance(self, obj):
        if hasattr(obj, "distance_val") and obj.distance_val:
            return f"{obj.distance_val.km:.2f} km"  # O obj.distance_val.m
        return None
