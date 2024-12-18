from django.db.models import Sum
from django.utils.timezone import now
from rest_framework import serializers

from event.models import Event, Category, TicketBatch, Booking


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class EventSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    class Meta:
        model = Event
        fields = ['id', 'category', 'host', 'name', 'description', 'start_date', 'end_date', 'location', 'address',
                  'max_attendance']
        read_only_fields = ['host']

    def validate(self, attrs):
        end_date = attrs['end_date']
        if end_date and end_date > attrs['start_date']:
            raise serializers.ValidationError("Start date must be before end date.")
        return attrs


class TicketBatchSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = TicketBatch
        fields = ['id', 'event', 'ticket_type', 'price', 'number_of_tickets', 'tickets_sold']
        read_only_fields = ['tickets_sold']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.context['request'].user
        self.fields['event'].queryset = Event.objects.filter(host=user)

    def validate(self, attrs):
        user = self.context['request'].user
        event = attrs['event']
        if event.host != user:
            raise serializers.ValidationError("You can only add ticket batches to events you host.")

        new_tickets = attrs['number_of_tickets']
        existing_tickets = TicketBatch.objects.filter(event=event).aggregate(
            total_tickets=Sum('number_of_tickets')
        )['total_tickets'] or 0

        # Ensure the total tickets do not exceed max_attendance
        max_attendance = event.max_attendance
        if existing_tickets + new_tickets > max_attendance:
            raise serializers.ValidationError(
                f"Total number of tickets ({existing_tickets + new_tickets}) exceeds the event's max attendance ({max_attendance})."
            )

        return attrs


class BookingSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = Booking
        fields = ['id', 'user', 'event', 'ticket_batch', 'ticket_count', 'payment_status', 'confirmed_at',
                  'cancelled_at', 'reference_code']
        read_only_fields = ['user', 'payment_status', 'confirmed_at', 'cancelled_at', 'reference_code']

    def validate(self, attrs):
        event = attrs['event']
        ticket_batch = attrs['ticket_batch']
        if ticket_batch.event != event:
            raise serializers.ValidationError("Ticket batch does not belong to the event.")
        if ticket_batch.tickets_sold >= ticket_batch.number_of_tickets:
            raise serializers.ValidationError("Ticket batch is sold out.")
        return attrs

    def create(self, validated_data):
        validated_data['payment_status'] = Booking.BookingStatusChoices.CONFIRMED
        validated_data['confirmed_at'] = now()

        return super().create(validated_data)


class QrCodeSerializer(serializers.ModelSerializer):
    qr_code_string = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ['qr_code_string']

    def get_qr_code_string(self, obj):
        return obj.generate_qr_string()
