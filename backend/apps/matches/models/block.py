import uuid

from django.db import models

from apps.users.models import Profile


class Block(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blocker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="blocks_given"
    )
    blocked = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="blocks_received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blocker", "blocked"], name="unique_block_pair"
            )
        ]

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
