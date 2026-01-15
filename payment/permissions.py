from rest_framework.permissions import BasePermission


class IsPaymentOwnerOrStaff(BasePermission):
    """
    Allows registered users to view only their own payments
    allows admins to view all payments
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_staff:
            return True
        return obj.borrowing.user_id == user.id
