import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class Swipe(models.Model):
    class SwipeType(models.TextChoices):
        LIKE = ("LIKE", _("Like"))
        DISLIKE = ("DISLIKE", _("Dislike"))
        SUPERLIKE = ("SUPER", _("Super Like"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Quién da el like
    swiper = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="swipes_made"
    )
    # A quién recibe el like
    target = models.ForeignKey(
        "users.Profile", on_delete=models.CASCADE, related_name="swipes_received"
    )

    value = models.CharField(max_length=10, choices=SwipeType.choices)
    # IMPORTANTE: db_index=True para que las consultas de "votos de hoy" sean rápidas
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        # La UniqueConstraint ya crea un índice interno en la BD
        # que sirve para búsquedas rápidas de la pareja (swiper, target).
        constraints = [
            models.UniqueConstraint(
                fields=["swiper", "target"], name="unique_swipe_between_users"
            )
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.swiper} -> {self.value} -> {self.target}"

    def save(self, *args, **kwargs):
        # Forzamos la validación antes de guardar
        self.clean()
        super().save(*args, **kwargs)

    def clean(self):
        """
        Validaciones de Lógica de Negocio en el Modelo.
        Esto impide datos corruptos incluso si se crean desde la consola de Python o el Admin.
        """
        super().clean()

        if self.swiper.id == self.target.id:
            raise ValidationError(_("No puedes darte like a ti mismo."))
