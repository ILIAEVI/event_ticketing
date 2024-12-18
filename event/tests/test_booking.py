from concurrent.futures.thread import ThreadPoolExecutor
from unittest.mock import patch
from django.db import IntegrityError, connection, transaction, connections
from rest_framework.test import APITestCase
from rest_framework import status
from event.models import TicketBatch, Booking, Event, Category
from authentication.models import User
from django.urls import reverse_lazy


class BookingViewSetTest(APITestCase):

    def setUp(self):
        self.category = Category.objects.create(name='Concert', is_active=True)
        self.host = User.objects.create_user(email='hostuser@gmail.com', password='password')
        self.event = Event.objects.create(
            category=self.category,
            host=self.host,
            name='Music Concert',
            location='Stadium',
            start_date='2024-12-25T12:00:00Z',
            end_date='2024-12-25T18:00:00Z',
            max_attendance=1000,
            is_active=True
        )
        self.ticket_batch = TicketBatch.objects.create(
            event=self.event,
            ticket_type='standard',
            price=50.00,
            number_of_tickets=100,
            tickets_sold=0
        )
        self.user = User.objects.create_user(email='testuser@gmail.com', password='password')
        self.client.login(email='testuser@gmail.com', password='password')

        self.valid_data = {
            'event': self.event.id,
            'ticket_batch': self.ticket_batch.id,
            'ticket_count': 10
        }

        self.url = reverse_lazy('booking-list')

    def test_successful_booking(self):
        # Test booking with valid data
        response = self.client.post(self.url, self.valid_data, format='json')
        # Assert the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)
        booking = Booking.objects.first()
        self.assertEqual(booking.ticket_count, 10)
        self.assertEqual(booking.payment_status, 'confirmed')
        self.assertEqual(booking.ticket_batch.tickets_sold, 10)

    @patch('event.models.TicketBatch.save')
    def test_booking_integrity_error(self, mock_save):
        mock_save.side_effect = IntegrityError("Simulated IntegrityError")

        response = self.client.post(self.url, self.valid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_booking_too_many_tickets(self):
        self.invalid_data = {
            'event': self.event.id,
            'ticket_batch': self.ticket_batch.id,
            'ticket_count': 200
        }

        response = self.client.post(self.url, self.invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
