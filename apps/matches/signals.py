from django.db import transaction
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from .models import Block, Match, Swipe


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


@receiver(post_save, sender=Block)
def delete_match_on_block(sender, instance: Block, created: bool, **kwargs):
    """
    Se ejecuta AUTOMÁTICAMENTE justo después de que un Block sea creado.
    Borra cualquier Match existente entre el bloqueador y el bloqueado.
    """
    if created:
        with transaction.atomic():
            blocker = instance.blocker
            blocked = instance.blocked

            # Buscar y borrar cualquier Match entre blocker y blocked
            Match.objects.filter(
                user_a__in=[blocker, blocked], user_b__in=[blocker, blocked]
            ).delete()
