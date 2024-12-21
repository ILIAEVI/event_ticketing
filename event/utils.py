from datetime import timedelta
import jwt
from django.utils import timezone
from django.conf import settings
from rest_framework.exceptions import PermissionDenied


def generate_booking_token(user, event):
    expiration_time = timezone.now() + timedelta(minutes=10)
    payload = {
        'user_id': user.id,
        'event_id': event.id,
        'expiration': expiration_time
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    return token


def validate_booking_token(token, event, user):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload['user_id'] != user.id or payload['event_id'] != event.id:
            raise PermissionDenied("Invalid token for this user or event.")
        expiration_time = payload['expiration']
        if timezone.now() > expiration_time:
            raise PermissionDenied("Token has expired.")

    except jwt.ExpiredSignatureError:
        raise PermissionDenied("Token has expired.")
    except jwt.InvalidTokenError:
        raise PermissionDenied("Invalid token.")
