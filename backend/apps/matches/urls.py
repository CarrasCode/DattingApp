from rest_framework.routers import DefaultRouter

from apps.matches.views import BlockViewSet, MatchViewSet, SwipeViewSet

router = DefaultRouter()
router.register(r"matches", MatchViewSet, basename="match")
router.register(r"swipes", SwipeViewSet, basename="swipe")
router.register(r"blocks", BlockViewSet, basename="block")


urlpatterns = router.urls
