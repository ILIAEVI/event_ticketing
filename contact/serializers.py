from rest_framework import serializers
from contact.models import ContactInfo, SocialMedia


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at']


class SendEmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100, required=True)
    message = serializers.CharField(required=True)
    contact_ids = serializers.ListField(child=serializers.IntegerField(), required=True, allow_empty=False,
                                        help_text="List of contact IDs to send email to.")


class SocialMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'name', 'url', 'icon']


class SocialMediaDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMedia
        fields = ['id', 'name', 'url', 'icon']

    def to_representation(self, instance):
        social_media_objects = SocialMedia.objects.all()
        return {social.id: social.url for social in social_media_objects}
