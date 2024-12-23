import secrets
import uuid
from django.core.cache import cache
from django.http import HttpRequest
from django.utils.cache import get_cache_key


def expire_page(path=''):
    request = HttpRequest()
    request.META['SERVER_NAME'] = 'localhost'
    request.META['SERVER_PORT'] = 8000
    request.path = path
    key = get_cache_key(request)
    if cache.has_key(key):
        cache.delete(key)


def generate_token():
    token = uuid.uuid4().hex + secrets.token_urlsafe(16)
    return token
