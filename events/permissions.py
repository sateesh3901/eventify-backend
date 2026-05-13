from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsHostOrReadOnly(BasePermission):
    """
    Hosts can create/edit/delete events.
    Everyone else can only read.
    """
    message = 'Only Hosts can create or modify events.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated and
            request.user.role == 'host'
        )


class IsEventOwner(BasePermission):
    """
    Only the host who created the event
    can edit or delete it.
    """
    message = 'You can only modify your own events.'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.host == request.user