from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.author == request.user or request.user.is_staff:
            return True
        raise PermissionDenied({'detail': 'У вас нет прав для доступа к этому объекту.'}, code=status.HTTP_401_UNAUTHORIZED)
