from rest_framework.permissions import BasePermission


class IsHostOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True

        if obj.__class__.__name__ == 'TicketBatch':
            return obj.event.host == request.user

        return obj.host == request.user


class IsBookingOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
