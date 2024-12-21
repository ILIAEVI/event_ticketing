from celery import shared_task
from django.db import transaction
from authentication.models import User
from event.models import TicketBatch, Booking
from event.queue_service import QueueService


@shared_task
def process_booking_queue(event_id):
    queue_service = QueueService(event=event_id)