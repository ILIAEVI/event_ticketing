from django.core.mail import send_mail
from rest_framework import viewsets, mixins, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from contact.filters import ContactListOrderingBackend
from contact.models import ContactInfo, SocialMedia
from contact.serializers import ContactInfoSerializer, SendEmailSerializer, SocialMediaSerializer, \
    SocialMediaDisplaySerializer


class ContactUsViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
    permission_classes = [permissions.AllowAny]


class ContactInfoViewSet(viewsets.ModelViewSet):
    queryset = ContactInfo.objects.all()
    serializer_class = ContactInfoSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filter_backends = [ContactListOrderingBackend]

    @action(
        detail=False,
        methods=['POST'],
        url_name="send_email",
        url_path="send_email",
        permission_classes=[permissions.IsAdminUser, permissions.IsAuthenticated],
        serializer_class=SendEmailSerializer
    )
    def send_email(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']
        contact_ids = serializer.validated_data['contact_ids']

        contacts = ContactInfo.objects.filter(id__in=contact_ids).values_list('email', flat=True)

        if not contacts.exists():
            return Response(
                {"error": "No contacts found with the given IDs."},
                status=status.HTTP_404_NOT_FOUND,
            )
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, list(contacts))
            return Response(
                {"success": f"Emails sent successfully!"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SocialMediaViewSet(viewsets.ModelViewSet):
    queryset = SocialMedia.objects.all().order_by('-id')
    serializer_class = SocialMediaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return SocialMediaDisplaySerializer
        return SocialMediaSerializer

    @method_decorator(cache_page(60 * 5))
    def retrieve(self, request, *args, **kwargs):
        """
        Cache the retrieve action
        """
        return super().retrieve(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 5))
    def list(self, request, *args, **kwargs):
        """
        Cache the list action
        """
        return super().list(request, *args, **kwargs)
