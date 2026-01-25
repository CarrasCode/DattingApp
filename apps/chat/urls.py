from rest_framework.routers import DefaultRouter

from .views import MessageViewSet

router = DefaultRouter()
# Ruta: /api/chat/messages/?match_id=...
router.register(r"messages", MessageViewSet, basename="messages")

urlpatterns = router.urls
