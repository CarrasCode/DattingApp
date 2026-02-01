import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.users.models import Profile


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Definimos explícitamente a los dos participantes
    user_a = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="matches_a"
    )
    user_b = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="matches_b"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        # Garantiza que solo exista UN match entre estas dos personas
        constraints = [
            models.UniqueConstraint(
                fields=["user_a", "user_b"], name="unique_match_pair"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Match {self.id}: {self.user_a} <-> {self.user_b}"

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.user_a == self.user_b:
            raise ValidationError(_("No puedes hacer match contigo mismo."))

        # Ordenar IDs
        # Si vienen desordenados, les damos la vuelta antes de guardar.
        # Esto asegura que siempre se guarde (ID_Menor, ID_Mayor).
        # Solo puede existir una única fila para representar la relación entre ellos dos,
        # sin importar quién "inició" el match.
        if self.user_a.id > self.user_b.id:
            self.user_a, self.user_b = self.user_b, self.user_a
