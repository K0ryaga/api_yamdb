from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or
                (request.user.is_authenticated and request.user.is_admin))


class AdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorAdminModerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_admin or request.user.is_moderator:
            return True

        if (request.method == 'PATCH' and obj.author == request.user) or (
                request.method == 'PATCH' and request.user.is_moderator):
            return True

        if request.method == 'DELETE' and obj.author == request.user:
            return True

        return False
