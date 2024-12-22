from django.db import models


class ContactInfo(models.Model):
    class SubjectChoices(models.TextChoices):
        GENERAL = 'general', 'General'
        FEEDBACK = 'feedback', 'Feedback'
        SUPPORT = 'support', 'Support'
        OTHER = 'other', 'Other'

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(
        max_length=255,
        choices=SubjectChoices.choices,
        default=SubjectChoices.GENERAL,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
