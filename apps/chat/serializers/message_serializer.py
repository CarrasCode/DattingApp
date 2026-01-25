from rest_framework import serializers

from apps.chat.models import Message


class MessageSerializer(serializers.ModelSerializer):
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ["id", "text", "is_me", "created_at", "is_read"]

    def get_is_me(self, obj):
        return obj.sender == self.context["request"].user
