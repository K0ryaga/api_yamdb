from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class AuthorModeratorAdminOrReadOnly(BasePermission):
    """Разрешение доступа на чтение всем и
    на редактирование только
    аутентифицированным пользователям"""

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or obj.author == user
            or user.is_admin
            or user.is_moderator
        )


class AdminReadOnly(BasePermission):
    """Разрешает получения списка всем и редактирование
    только  администратору/суперпользователю"""

    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in SAFE_METHODS
            or (user.is_authenticated and user.is_admin)
        )


class AdminPermission(permissions.BasePermission):
    """Разрешает только администратору"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorAdminModerOrReadOnly(permissions.BasePermission):
    """Разрешает только администратору, модератору и автору."""
    def has_permission(self, request, view):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            request.method in permissions.SAFE_METHODS
            or user.is_admin
            or user.is_moderator
            or obj.author == user
            or (request.method == 'PATCH' and (
                obj.author == user or user.is_moderator))
            or (request.method == 'DELETE' and obj.author == user)
        )
