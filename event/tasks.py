from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from event.models import EventQueue, BookingToken
from event.queue_service import QueueService

TOKEN_EXPIRY_TIME = 60 * 10


@shared_task
def process_event_queue():
    BookingToken.objects.filter(created_at__lte=timezone.now() - timedelta(seconds=TOKEN_EXPIRY_TIME)).delete()
    event = EventQueue.objects.get(is_active=True)
    if event:
        queue_service = QueueService(event=event)
        user_ids = queue_service.process_queue()
        booking_tokens = [BookingToken(user_id=user_id, event=event) for user_id in user_ids]
        if booking_tokens:
            BookingToken.objects.bulk_create(booking_tokens)
            print("Booking tokens created successfully.")
    print("Event Queue processed successfully.")
