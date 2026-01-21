from typing import Any

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Asume que el modelo tiene un atributo o property 'owner'
    que devuelve el objeto usuario.
    - GET, HEAD, OPTIONS (Lectura) -> Permitido a cualquier usuario autenticado.
    - PUT, PATCH, DELETE (Escritura) -> Solo permitido si el usuario es el dueño.

    """

    def has_object_permission(self, request, view, obj) -> Any:
        # 1. Si el método es seguro (solo lectura), dejamos pasar.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Si quiere editar, comprobamos si el usuario de la petición
        # es el dueño del objeto.
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        return False


class HasProfile(permissions.BasePermission):
    message = "Debes crear un perfil antes de realizar esta acción."

    def has_permission(self, request, view) -> Any:
        # Si no está logueado, fallará IsAuthenticated primero, así que aquí asumimos que lo está.
        return hasattr(request.user, "profile")
