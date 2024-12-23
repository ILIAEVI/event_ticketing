from django.contrib import admin
from event.models import Event, Category, TicketBatch, Booking, EventQueue, BookingToken

admin.site.register(Event)
admin.site.register(EventQueue)
admin.site.register(Category)
admin.site.register(Booking)
admin.site.register(BookingToken)
admin.site.register(TicketBatch)

