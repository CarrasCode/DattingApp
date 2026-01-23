from rest_framework import serializers

from apps.matches.models import Block


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ["id", "owner", "blocked_user", "created_at"]
        read_only_fields = ["owner", "created_at"]
