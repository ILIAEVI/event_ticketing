from rest_framework import viewsets, permissions
from rest_framework.viewsets import mixins
from event.serializers import EventSerializer, CategorySerializer, TicketBatchSerializer
from event.models import Event, Category, TicketBatch


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-id')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class TicketBatchViewSet(viewsets.ModelViewSet):
    queryset = TicketBatch.objects.all()
    serializer_class = TicketBatchSerializer
    permission_classes = [permissions.IsAuthenticated]


