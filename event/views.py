from django.db import transaction
from django.db.models import F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import mixins
from event.permissions import IsHostOrReadOnly, IsBookingOwner
from event.queue_service import QueueService
from event.serializers import EventSerializer, CategorySerializer, TicketBatchSerializer, BookingSerializer, \
    QrCodeSerializer
from event.models import Event, Category, TicketBatch, Booking, BookingToken


class CategoryViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-id')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsHostOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        """
        Cache the retrieve action for event details
        """
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        """
        Cache the list action for all events
        """
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['get'],
        url_path='start_booking',
        url_name='start_booking',
        permission_classes=[permissions.IsAuthenticated]
    )
    def start_booking(self, request, pk=None):
        """
        if event queue is active, add user to queue
        else, allow booking.
        """
        user = self.request.user
        event = self.get_object()
        event_queue = event.event_queue
        if event_queue and event_queue.is_active:
            booking_token = BookingToken.objects.filter(user=user, event=event.event_queue).first()
            if booking_token and booking_token.is_valid():
                return Response({"message": "You are allowed to continue booking"}, status=status.HTTP_200_OK)
            queue_service = QueueService(event=event)
            if queue_service.add_to_queue(str(user.id)):
                return Response({"message": "You have been added to the waiting room"}, status=status.HTTP_201_CREATED)
            return Response({"message": "You are already in the queue"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "The EventQueue is not active, You are allowed to continue booking"},
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        serializer_class=BookingSerializer,
        url_path='booking',
        url_name='booking',
        permission_classes=[permissions.IsAuthenticated]
    )
    def booking(self, request, pk=None):
        """
        check and validate booking tokens if event queue is active.
        there is used transaction.atomic() to avoid race condition.
        """
        event = self.get_object()
        user = self.request.user
        event_queue = event.event_queue
        if event_queue and event_queue.is_active:
            queue_token = BookingToken.objects.filter(user=user, event=event.event_queue).first()
            if not queue_token:
                raise PermissionDenied("Queue Token is required to continue booking.")
            if not queue_token.is_valid():
                print("Queue Token is expired.")
                raise PermissionDenied("Queue Token is expired.")

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
        url_name='queue',
        permission_classes=[permissions.IsAuthenticated]
    )
    def queue(self, request, pk=None):
        """
        waiting room imitation, return users' position in queue.
        if user is in allowed users return booking token.
        """
        user = self.request.user
        event = self.get_object()
        queue_service = QueueService(event=event)
        position = queue_service.get_user_position(str(user.id))
        allowed_users = queue_service.get_allowed_users()

        if str(user.id) in allowed_users:
            booking_token = BookingToken.objects.get(user=user, event=event.event_queue).token
            return Response(
                {"message": "You are allowed to start the booking",
                 "booking_token": booking_token},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"message": "Your are in the queue", "position": position},
            status=status.HTTP_200_OK,
        )


class TicketBatchViewSet(viewsets.ModelViewSet):
    queryset = TicketBatch.objects.all()
    serializer_class = TicketBatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsHostOrReadOnly]


class BookingViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Booking.objects.all().order_by('-id')
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)

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
