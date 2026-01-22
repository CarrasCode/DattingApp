from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from serializers import MatchSerializer, SwipeSerializer
from services.match_service import create_swipe_and_check_match

from apps.users.permissions import HasProfile


class SwipeViewSet(viewsets.GenericViewSet):
    """
    Solo permitimos CREAR swipes (POST).
    No tiene sentido listar o editar swipes pasados.
    """

    serializer_class = SwipeSerializer
    permission_classes = [IsAuthenticated, HasProfile]

    def create(self, request, *args, **kwargs):
        # 1. Validar datos de entrada (Input)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 2. Llamar a la Capa de Servicio (Lógica de Negocio)
        # El serializer nos da los datos limpios (validated_data)
        target_profile = serializer.validated_data["target"]
        value = serializer.validated_data["value"]

        swipe, match = create_swipe_and_check_match(
            swiper=request.user.profile, target=target_profile, value=value
        )

        # 3. Preparar respuesta (Output)
        response_data = {"match": match is not None, "swipe_id": swipe.id}

        if match:
            # Si hubo match, serializamos el match para devolverlo
            match_serializer = MatchSerializer(match, context={"request": request})
            response_data["match_details"] = match_serializer.data

        return Response(response_data, status=status.HTTP_201_CREATED)
