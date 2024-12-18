from django.db import transaction, IntegrityError
from django.db.models import F
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from event.permissions import IsHostOrReadOnly, IsBookingOwner
from event.serializers import EventSerializer, CategorySerializer, TicketBatchSerializer, BookingSerializer, \
    QrCodeSerializer
from event.models import Event, Category, TicketBatch, Booking


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-id')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsHostOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)


class TicketBatchViewSet(viewsets.ModelViewSet):
    queryset = TicketBatch.objects.all()
    serializer_class = TicketBatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostOrReadOnly]


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all().order_by('-id')
    serializer_class = BookingSerializer
    #permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        ticket_batch = serializer.validated_data['ticket_batch']
        ticket_count = serializer.validated_data['ticket_count']
        try:
            with transaction.atomic():
                ticket_batch = TicketBatch.objects.select_for_update().get(id=ticket_batch.id)
                if ticket_batch.tickets_sold + ticket_count > ticket_batch.number_of_tickets:
                     raise ValidationError("Not enough tickets available for booking.")
                ticket_batch.tickets_sold = F('tickets_sold') + ticket_count
                ticket_batch.save()
                serializer.save(user=user)
        except IntegrityError:
            raise ValidationError("An error occurred while processing your booking.")

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated, IsBookingOwner],
        serializer_class=QrCodeSerializer,
        url_path='get-qr-code',
        url_name='get-qr-code'
    )
    def get_qr_code(self, request, pk=None):
        booking = self.get_object()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)
