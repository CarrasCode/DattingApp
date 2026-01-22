from models import Match, Swipe
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers import MatchSerializer, SwipeSerializer


class SwipeViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    Solo permitimos CREAR swipes (POST).
    No tiene sentido listar o editar swipes pasados.
    """

    serializer_class = SwipeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # 1. Validación estándar del Serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Guardamos el Swipe en la base de datos
        # El serializer ya sabe inyectar al 'swiper' (usuario actual)
        swipe_instance = serializer.save()

        # 3. EL ALGORITMO DE MATCH 💘
        # Inicializamos variable de retorno
        match_data = None
        is_match = False

        # Solo buscamos match si yo di LIKE o SUPERLIKE (si di DISLIKE, da igual lo que piense el otro)
        if swipe_instance.value in [Swipe.SwipeType.LIKE, Swipe.SwipeType.SUPERLIKE]:
            # Pregunta a la BD: "¿Existe un swipe del OTRO hacia MÍ que sea positivo?"
            reciprocal_swipe = Swipe.objects.filter(
                swiper=swipe_instance.target,  # El otro es el creador
                target=swipe_instance.swiper,  # Yo soy el objetivo
                value__in=[Swipe.SwipeType.LIKE, Swipe.SwipeType.SUPERLIKE],
            ).exists()

            if reciprocal_swipe:
                is_match = True
                # ¡BINGO! Creamos el Match
                match = Match.objects.create()
                match.users.add(swipe_instance.swiper, swipe_instance.target)

                # Preparamos los datos del match para que el frontend pueda mostrar
                # "It's a Match!" con la foto de la otra persona inmediatamente.
                # Pasamos el contexto 'request' para que el serializer pueda calcular URL de fotos
                match_data = MatchSerializer(match, context={"request": request}).data

        # 4. Respuesta Personalizada
        return Response(
            {
                "match": is_match,
                "match_details": match_data,  # Será null si no hubo match
                "swipe_id": swipe_instance.id,
            },
            status=status.HTTP_201_CREATED,
        )
