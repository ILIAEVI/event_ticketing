from datetime import timedelta
from django.conf import settings
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken


def generate_email_verification_token(user):
    refresh = RefreshToken.for_user(user)
    refresh.set_exp(lifetime=timedelta(minutes=10))
    return str(refresh.access_token)


def send_verification_email(user, verification_url):
    subject = "Email Verification"
    message = f"Hi {user.email}, \n\nPlease verify your email by clicking the link below:\n\n{verification_url}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def send_password_reset_email(user, verification_url):
    subject = "Password Reset"
    message = f"Hi {user.email}, \n\nYou can reset your password by clicking the link below:\n\n{verification_url}"
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
