import uuid

from django.db import models

from apps.matches.models import Match
from apps.users.models import Profile


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Sala del chat
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="messages")

    sender = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="sent_messages"
    )

    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["match", "created_at"]
            ),  # Index para optimizar consultas por sala y fecha
        ]

    def __str__(self):
        return f"Message {self.id} in match {self.match.id} "
