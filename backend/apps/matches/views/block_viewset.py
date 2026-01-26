from typing import Any

from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.matches.models import Block
from apps.matches.serializers import BlockSerializer


class BlockViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset for viewing and editing block instances.
    """

    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> Any:
        user: Any = self.request.user
        profile = user.profile
        return Block.objects.filter(blocker=profile)
