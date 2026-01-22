from django.db import transaction
from models import Match, Swipe

from apps.users.models import Profile


def create_swipe_and_check_match(swiper: Profile, target: Profile, value: str):
    """
    Orquesta la creación del Swipe y verifica si hay Match.
    Retorna una tupla: (swipe_instance, match_instance_o_None)
    """

    # Usamos atomicidad: O se hace todo bien, o no se hace nada en la BD
    with transaction.atomic():
        # 1. Crear el Swipe
        swipe = Swipe.objects.create(swiper=swiper, target=target, value=value)

        match = None

        # 2. Lógica de Match (Solo si es Like/Superlike)
        if value in [Swipe.SwipeType.LIKE, Swipe.SwipeType.SUPERLIKE]:
            # Bloqueamos la fila del swipe recíproco para evitar que otro proceso
            # intente crear un match al mismo tiempo (Race condition)
            is_reciprocal = (
                Swipe.objects.select_for_update()
                .filter(
                    swiper=target,  # El que recibe ahora, fue el que dio like antes
                    target=swiper,
                    value__in=[Swipe.SwipeType.LIKE, Swipe.SwipeType.SUPERLIKE],
                )
                .exists()
            )

            if is_reciprocal:
                # Verificamos si ya existe un match por si acaso
                # Ordenamos user_a y user_b por ID para mantener consistencia en la BD
                # Aunque se revise esto en el model, es convenient tambien revisarlo aqui
                user_a, user_b = sorted([swiper, target], key=lambda x: x.id)
                # En caso de que dos usuarios hagan match a la vez.
                match = Match.objects.get_or_create(user_a=user_a, user_b=user_b)

        return swipe, match
