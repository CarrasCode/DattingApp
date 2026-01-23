from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.matches.models import Block
from apps.matches.serializers import BlockSerializer


class BlockViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing block instances.
    """

    queryset = Block.objects.all()
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
