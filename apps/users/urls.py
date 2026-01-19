from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProfileViewSet, UserRegistrationView

# El router crea automáticamente:
# GET /profiles/ -> Lista
# GET /profiles/{id}/ -> Ver detalle
# PUT /profiles/{id}/ -> Editar
# GET /profiles/me/ -> Nuestra acción personalizada
router = DefaultRouter()
router.register(r"profiles", ProfileViewSet, basename="profile")

urlpatterns = [
    # Auth endpoints
    path("auth/register/", UserRegistrationView.as_view(), name="register"),
    # Profile endpoints (generados por el router)
    path("", include(router.urls)),
]
