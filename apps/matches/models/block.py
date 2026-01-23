from django.db import models

from apps.users.models import Profile


class Block(models.Model):
    blocker = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="blocks_given"
    )
    blocked = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="blocks_received"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")

    def __str__(self):
        return f"{self.blocker} blocked {self.blocked}"
