from django.urls import path, include
from rest_framework.routers import DefaultRouter
from event.views import EventViewSet, CategoryViewSet, TicketBatchViewSet

router = DefaultRouter()

router.register(r'event', EventViewSet, basename='event')
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'ticket_batch', TicketBatchViewSet, basename='ticket_batch')

urlpatterns = [
    path('', include(router.urls)),
]
