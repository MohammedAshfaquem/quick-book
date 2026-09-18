from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    message = "Staff access required."

    def has_permission(self, request, view):
        """Return True only for authenticated staff users."""
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOwnerOrStaff(BasePermission):
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        """Return True if request.user owns the object or is staff."""
        return obj.user == request.user or request.user.is_staff
