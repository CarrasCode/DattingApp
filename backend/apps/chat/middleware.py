"""
JWT Authentication Middleware for Django Channels WebSockets.

Usage:
    Frontend connects with: ws://host/ws/chat/123/?token=<jwt_access_token>
"""

from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.users.models import CustomUser


@database_sync_to_async
def get_user_from_token(token_str: str) -> CustomUser | AnonymousUser:
    """
    Valida el token JWT y devuelve el usuario asociado.
    Si el token es inválido o el usuario no existe, devuelve AnonymousUser.
    """
    try:
        # Decodifica y valida el token
        access_token = AccessToken(token_str)  # type: ignore
        user_id = access_token["user_id"]
        return CustomUser.objects.get(id=user_id)
    except (InvalidToken, TokenError, ObjectDoesNotExist, KeyError):
        return AnonymousUser()


class JWTAuthMiddleware(BaseMiddleware):
    """
    Middleware que autentica conexiones WebSocket usando JWT.
    El token se pasa como query parameter: ?token=xxx
    """

    async def __call__(self, scope, receive, send):
        # Extraer query string del scope
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)

        # Obtener el token (parse_qs devuelve listas)
        token_list = query_params.get("token", [])
        token = token_list[0] if token_list else None

        if token:
            scope["user"] = await get_user_from_token(token)
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
