from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
    # --- NUEVOS ENDPOINTS PARA LOGIN (JWT) ---
    path("auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Profile endpoints (generados por el router)
    path("", include(router.urls)),
]
