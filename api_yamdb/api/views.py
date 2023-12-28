from rest_framework import status, viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import IntegrityError
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .serializers import (
    UserEditSerializer,
    TokenSerializer,
    RegistrationSerializer,
    CategorySerializer,
    UserSerializer,
    GenreSerializer)
from reviews.models import Category, User, Genre
from reviews.permissions import IsAuthorAdminModerOrReadOnly, AdminPermission
from .pagination import CustomPageNumberPagination


class GetPostDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


@api_view(['POST'])
def sign_up(request):
    # Если можно обойтись без использования try-except, то лучше обойтись без него, т.к. обработка исключения занимает достаточно много времени.
    serializer = RegistrationSerializer(data=request.data)
    email = request.data.get('email')
    serializer.is_valid(raise_exception=True)
    try:
        user, created = User.objects.get_or_create(**serializer.validated_data)
    except IntegrityError:
        return Response(
            'Попробуй другой email или username',
            status=status.HTTP_400_BAD_REQUEST,
        )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        'Token Token Token',
        confirmation_code,
        'Yamdb',
        [email],
        fail_silently=False,)
    return Response(serializer.data, status=status.HTTP_200_OK)


class TokenApiView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.initial_data.get('username')
            user = get_object_or_404(User, username=username)
            confirmation_code = serializer.initial_data.get(
                'confirmation_code'
            )
            if not default_token_generator.check_token(
                user, confirmation_code
            ):
                return Response(
                    'Неправильный код', status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_201_CREATED,
            )
        return Response('Error', status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(GetPostDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = CustomPageNumberPagination
    post_data = {'name': 'Книги', 'slug': 'books'}

    def list(self, request, *args, **kwargs):
        # Можно использовать стандартный функционал DRF для сериализации
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (AdminPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        user = get_object_or_404(User, username=self.request.user)
        serializer = UserEditSerializer(user)
        if request.method == 'PATCH':
            serializer = UserEditSerializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if User.objects.filter(**serializer.validated_data).exists():
            return Response(
                'Попробуй другой email или username',
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(**serializer.validated_data)
        serialized_user = UserSerializer(user).data
        return Response(
            serialized_user,
            status=status.HTTP_201_CREATED
        )


class GenreViewSet(GetPostDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthorAdminModerOrReadOnly]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)
