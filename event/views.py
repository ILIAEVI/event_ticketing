from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from event.permissions import IsHostOrReadOnly, IsBookingOwner
from event.queue_service import QueueService
from event.serializers import EventSerializer, CategorySerializer, TicketBatchSerializer, BookingSerializer, \
    QrCodeSerializer
from event.models import Event, Category, TicketBatch, Booking
from event.utils import generate_booking_token, validate_booking_token


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-id')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsHostOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=BookingSerializer,
        url_path='booking',
        url_name='booking',
        # permission_classes=[permissions.IsAuthenticated]
    )
    def booking(self, request, pk=None):
        event = self.get_object()
        user = self.request.user
        queue_token = request.headers.get('queue_token')
        if not queue_token:
            raise PermissionDenied("Queue Token is required")

        validate_booking_token(queue_token, event=event, user=user)

        serializer = self.get_serializer(data=request.data, context={'event': event, 'user': user})
        serializer.is_valid(raise_exception=True)

        ticket_batch = serializer.validated_data['ticket_batch']
        ticket_count = serializer.validated_data['ticket_count']
        try:
            with transaction.atomic():
                ticket_batch = TicketBatch.objects.select_for_update().get(id=ticket_batch.id)
                if ticket_batch.tickets_sold + ticket_count > ticket_batch.number_of_tickets:
                    raise ValidationError("Not enough tickets available for booking.")
                if ticket_batch.tickets_sold == ticket_batch.number_of_tickets:
                    raise ValidationError("Ticket batch is sold out.")
                ticket_batch.tickets_sold = F('tickets_sold') + ticket_count
                ticket_batch.save()
                serializer.save(event=event, user=user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except TicketBatch.DoesNotExist:
            raise ValidationError("The ticket batch for this event does not exist.")
        except Exception as e:
            raise ValidationError("An error occurred while processing your booking.", e)

    @action(
        detail=True,
        methods=['get'],
        url_path='queue',
        url_name='queue'
    )
    def queue(self, request, pk=None):
        user = self.request.user
        event = self.get_object()
        queue_service = QueueService(event=event)
        if queue_service.add_to_queue(str(user.id)):
            return Response({"message": "You have been added to the queue."}, status=status.HTTP_200_OK)
        position = queue_service.get_user_position(str(user.id))
        if position == 1:
            queue_service.process_queue()
            token = generate_booking_token(user, event)
            return Response({"queue_token": token}, status=status.HTTP_200_OK)
        return Response(
            {"message": "You are currently in the queue.", "position": position},
            status=status.HTTP_200_OK,
        )


class TicketBatchViewSet(viewsets.ModelViewSet):
    queryset = TicketBatch.objects.all()
    serializer_class = TicketBatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostOrReadOnly]


class BookingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Booking.objects.all().order_by('-id')
    serializer_class = BookingSerializer

    # permission_classes = [permissions.IsAuthenticated]

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
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
