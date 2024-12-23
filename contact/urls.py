from django.urls import path, include
from rest_framework.routers import DefaultRouter
from contact.views import ContactInfoViewSet, ContactUsViewSet, SocialMediaViewSet

router = DefaultRouter()
router.register(r'contact_us', ContactUsViewSet, basename='contact_us')
router.register(r'contacts', ContactInfoViewSet, basename='contacts')

router.register(r'social_media', SocialMediaViewSet, basename='social_media')

urlpatterns = [
    path('', include(router.urls)),
]
