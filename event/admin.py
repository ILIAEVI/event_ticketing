from django.contrib import admin
from event.models import Event, Category, TicketBatch, Booking

admin.site.register(Event)
admin.site.register(Category)
admin.site.register(Booking)
admin.site.register(TicketBatch)

