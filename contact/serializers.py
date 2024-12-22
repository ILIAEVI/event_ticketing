from rest_framework import serializers
from contact.models import ContactInfo


class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at']


class SendEmailSerializer(serializers.Serializer):
    subject = serializers.CharField(max_length=100, required=True)
    message = serializers.CharField(required=True)
    contact_ids = serializers.ListField(child=serializers.IntegerField(), required=True, allow_empty=False,
                                        help_text="List of contact IDs to send email to.")
