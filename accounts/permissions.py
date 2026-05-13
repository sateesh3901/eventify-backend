from rest_framework.permissions import BasePermission


class IsHost(BasePermission):
    """
    Allow access only to users with 'host' role.
    """
    message = 'Access restricted to Hosts only.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'host'
        )


class IsAdminUser(BasePermission):
    """
    Allow access only to users with 'admin' role.
    """
    message = 'Access restricted to Admins only.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Allow access to object owner or admin only.
    """
    message = 'You do not have permission to perform this action.'

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            (obj == request.user or request.user.role == 'admin')
        )