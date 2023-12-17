from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.http import HttpResponse
from rest_framework import filters, viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
import string
import random

from core.permissions import (
    IsAdminOrReadOnly,
    IsAuthorModeratorAdminOrReadOnly,
)
from reviews.models import Category, Genre, Review, Title, User
from .filters import TitleFilter
from .mixins import GetListCreateDeleteMixin
from .permissions import IsReviewOwnerOrModeratorOrAdmin, IsAdminUser
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleRetrieveSerializer,
    TitleWriteSerializer,
    UserSignupSerializer,
)


def code_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class UserSignupViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = []
    allowed_methods = ['POST']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        confirmation_code = code_generator()
        if serializer.is_valid() is False:
            User(confirmation_code=confirmation_code).save
        else:
            serializer.save(confirmation_code=confirmation_code)

        send_mail(
            subject='Confirmation code',
            message=f'Your confirmation code is {confirmation_code}',
            from_email='from@example.com',
            recipient_list=[request.data.get('email')],
            fail_silently=True,
        )
        return HttpResponse("На почту был отправлен код подтверждения")


class UserSignupByAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    allowed_methods = ['POST']
    permission_classes = (IsAdminUser,)


class CommentViewSet(ModelViewSet):
    """
    Получить список всех комментариев.
    Добавление нового комментария к отзыву.
    Получить комментарий по id.
    Обновление комментария по id.
    Удаление комментария.
    """

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorModeratorAdminOrReadOnly,)
    http_method_names = ("get", "post", "delete", "patch")

    def get_review(self):
        return get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title_id=self.kwargs.get("title_id"),
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведения."""

    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = ("get", "post", "delete", "patch")

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleRetrieveSerializer
        return TitleWriteSerializer


class CategoryViewSet(GetListCreateDeleteMixin):
    """Вьюсет для категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(GetListCreateDeleteMixin):
    """Вьюсет для жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrModeratorOrAdmin]
    lookup_field = 'title_id'
