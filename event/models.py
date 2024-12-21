import uuid
from django.db import models
from django.db.models import F
from rest_framework.exceptions import ValidationError

from authentication.models import User


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
