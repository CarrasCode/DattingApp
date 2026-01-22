from models import Match
from rest_framework import serializers

from apps.users.serializers import PublicProfileSerializer


class MatchSerializer(serializers.ModelSerializer):
    other_user = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = ["id", "created_at", "other_user"]
        read_only_fields = ["id", "created_at", "other_user"]

    def get_other_user(self, obj: Match):
        """
        Determina dinámicamente quién es la 'otra' persona en el match.
        """
        request = self.context.get("request")

        # Si no hay request o usuario, retornamos None
        if not request or not hasattr(request, "user"):
            return None

        my_profile_id = request.user.profile.id
        target_profile = None

        # Usar getattr para que el linter no se queje de atributos dinámicos
        user_a_id = getattr(obj, "user_a_id", None)
        user_b_id = getattr(obj, "user_b_id", None)

        if user_a_id == my_profile_id:
            target_profile = obj.user_b
        elif user_b_id == my_profile_id:
            target_profile = obj.user_a

        if target_profile:
            # Pasamos el contexto al serializador anidado.
            # Crucial para que ImageFields generen URLs absolutas correctamente.
            return PublicProfileSerializer(target_profile, context=self.context).data

        return None
