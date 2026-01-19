from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    - GET, HEAD, OPTIONS (Lectura) -> Permitido a cualquier usuario autenticado.
    - PUT, PATCH, DELETE (Escritura) -> Solo permitido si el usuario es el dueño.
    """

    def has_object_permission(self, request, view, obj):
        # 1. Si el método es seguro (solo lectura), dejamos pasar.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Si quiere editar, comprobamos si el usuario de la petición
        # es el dueño del objeto.
        return obj.custom_user == request.user
