from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..serializers import UserRegistrationSerializer


# --- VISTA DE REGISTRO (CreateAPIView) ---
# Usamos CreateAPIView porque solo queremos una acción: POST.
# No necesitamos listar usuarios ni borrarlos aquí.
class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Importante: El registro debe ser público


class LogoutView(APIView):
    """
    Vista para cerrar sesión.
    Recibe el 'refresh_token' y lo pone en la lista negra para que no pueda volver a usarse.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            raise ValidationError({"detail": "El campo 'refresh' es obligatorio."})

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            raise ValidationError({"detail": "Token inválido o expirado."}) from None
