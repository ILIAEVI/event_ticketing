import uuid
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from authentication.models import User
from event.utils import generate_token, expire_page, expire_view_cache


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Event(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    location = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True, blank=True)
    max_attendance = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class TicketBatch(models.Model):
    class TicketTypeChoices(models.TextChoices):
        STANDARD = 'standard', 'Standard'
        VIP = 'vip', 'VIP'
        DISCOUNT = 'discount', 'Discount'

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='ticket_batches')
    ticket_type = models.CharField(choices=TicketTypeChoices.choices, default=TicketTypeChoices.STANDARD)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    number_of_tickets = models.PositiveIntegerField(default=0)
    tickets_sold = models.PositiveIntegerField(default=0)


class Booking(models.Model):
    class BookingStatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='bookings')
    ticket_batch = models.ForeignKey(TicketBatch, on_delete=models.CASCADE, related_name='bookings')
    ticket_count = models.PositiveIntegerField(default=1)
    payment_status = models.CharField(choices=BookingStatusChoices.choices, default=BookingStatusChoices.PENDING)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    reference_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def generate_qr_string(self):
        """Generate QR string for QR code."""
        qr_data = f"Booking ID: {self.id}, Reference Code: {self.reference_code}, Event: {self.event.name}, User: {self.user.email}"
        return qr_data


class Feedback(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1 to 5
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class EventQueue(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='event_queue')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.event} Event Queue"

    def save(self, *args, **kwargs):
        """
            At this development stage, only one EventQueue can be active at a time.
            If the current EventQueue is being set as active, all others are deactivated.
        """
        if self.is_active:
            EventQueue.objects.filter(is_active=True).update(is_active=False)

        super().save(*args, **kwargs)


class BookingToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='booking_tokens')
    event = models.ForeignKey(EventQueue, on_delete=models.CASCADE, related_name='booking_tokens')
    token = models.CharField(max_length=255, default=generate_token, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (timezone.now() - self.created_at).total_seconds() < 600

    def __str__(self):
        return f"{self.token}"


@receiver(post_save, sender=Event)
@receiver(post_delete, sender=Event)
def clear_event_cache(sender, instance, **kwargs):

    expire_view_cache('event-list')