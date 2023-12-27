from rest_framework import viewsets, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .permissions import IsAdminOrReadOnly, IsAuthorAdminModerOrReadOnly
from api.filters import TitleFilter
from .serializers import (
    TitleSerializer,
    TitleSerializerWrite,
    ReviewSerializer,
    CommentSerializer,)
from reviews.models import (Title,
                            Review,)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet модели Title."""

    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleSerializerWrite

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        elif request.method == 'PATCH':
            return super().update(request, *args, **kwargs)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModerOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(title=title, author=self.request.user)

    @property
    def allowed_methods(self):
        methods = super().allowed_methods
        return [m for m in methods if m != 'PUT']

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment"""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModerOrReadOnly,)
    pagination_class = PageNumberPagination

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(
            review=self.get_review(), author=self.request.user
        )

    @property
    def allowed_methods(self):
        methods = super().allowed_methods
        return [m for m in methods if m != 'PUT']

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.author == request.user:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.user.is_moderator:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if request.user.is_admin:
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        raise PermissionDenied()
