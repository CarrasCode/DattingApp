from rest_framework import serializers

from apps.matches.models import Block

from .swipe_serializer import CurrentProfileDefault


class BlockSerializer(serializers.ModelSerializer):
    blocker = serializers.HiddenField(default=CurrentProfileDefault())

    class Meta:
        model = Block
        fields = ["id", "blocker", "blocked", "created_at"]
        read_only_fields = ["id", "created_at"]
