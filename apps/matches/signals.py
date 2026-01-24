from django.db import transaction
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Match, Swipe


@receiver(pre_delete, sender=Match)
def convert_likes_to_dislikes_on_unmatch(sender, instance: Match, **kwargs):
    """
    Se ejecuta AUTOMÁTICAMENTE justo antes de que un Match sea borrado.
    Convierte los Swipes originales en DISLIKE.
    """
    # Usamos transaction.atomic por seguridad, aunque signal suele ir en la tx del delete
    with transaction.atomic():
        # instance es el objeto Match que está a punto de morir
        # OJO: Usamos pre_delete porque en post_delete la relación ManyToMany ya se habría roto
        user_a = instance.user_a
        user_b = instance.user_b

        if user_a and user_b:
            # Actualizamos masivamente (Bulk Update)
            # Buscamos Swipes entre A y B (en ambas direcciones)
            Swipe.objects.filter(
                swiper__in=[user_a, user_b], target__in=[user_a, user_b]
            ).update(value=Swipe.SwipeType.DISLIKE)
