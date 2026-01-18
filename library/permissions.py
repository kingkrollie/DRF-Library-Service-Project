from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrStaff(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and (request.user.is_staff or obj.user_id == request.user.id)
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Allow read-only access for any request.
    Write permissions are only allowed to admin users.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return bool(request.user and request.user.is_staff)
