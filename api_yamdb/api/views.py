from rest_framework import status, viewsets, mixins, filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Avg,  Q
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
    GenreSerializer,
    TitleSerializer,
    TitleSerializerWrite,
    ReviewSerializer,
    CommentSerializer,)
from reviews.models import (Category,
                            User,
                            Genre,
                            Title,
                            Review,)
from .permissions import (IsAuthorAdminModerOrReadOnly,
                          AdminPermission,
                          AdminReadOnly,)
from .filters import TitleFilter


class GetPostDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                           mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


@api_view(['POST'])
def sign_up(request):
    serializer = RegistrationSerializer(data=request.data)
    email = request.data.get('email')
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    user = User.objects.filter(Q(username=username) | Q(email=email)).first()

    if user and user.email != serializer.data['email']:
        return Response(
            {'username': 'Такой username уже зарегистрирован'},
            status=status.HTTP_400_BAD_REQUEST
        )

    elif user and user.username != serializer.data['username']:
        return Response(
            {'email': 'Такой email уже зарегистрирован'},
            status=status.HTTP_400_BAD_REQUEST
        )

    elif user is None:
        user = User.objects.create_user(**serializer.validated_data)
        user.is_staff = True
        user.save()
        confirmation_code = default_token_generator.make_token(user)

        send_mail(
            'Token Token Token',
            confirmation_code,
            'Yamdb',
            [email],
            fail_silently=False,
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.data, status=status.HTTP_200_OK)


class TokenApiView(APIView):
    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.initial_data.get('username')
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(
                    status=status.HTTP_404_NOT_FOUND,
                    data={'username': 'Incorrect code'}
                )
            confirmation_code = serializer.initial_data.get(
                'confirmation_code'
            )
            if not default_token_generator.check_token(
                user, confirmation_code
            ):
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'confirmation_code': 'Incorrect code'}
                )
            token = RefreshToken.for_user(user)
            return Response(
                {'token': str(token.access_token)},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(GetPostDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AdminReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'


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

        user = serializer.validated_data.get('username')
        if User.objects.filter(username=user).exists():
            return Response(
                'Пользователь с таким username уже существует',
                status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(**serializer.validated_data)
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthorAdminModerOrReadOnly,
        permissions.IsAuthenticatedOrReadOnly)
    pagination_class = PageNumberPagination
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    @property
    def allowed_methods(self):
        methods = super().allowed_methods
        return [m for m in methods if m != 'PUT']

    def update(self, request, *args, **kwargs):
        if request.method == 'PATCH':
            return super().update(request, *args, **kwargs)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(GetPostDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (AdminReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PageNumberPagination


class TitleViewSet(viewsets.ModelViewSet):

    http_method_names = ['get', 'post', 'patch', 'delete']

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('id')
    permission_classes = (AdminReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleSerializer
        return TitleSerializerWrite

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        created_item = Title.objects.get(pk=serializer.data['id'])
        response_serializer = TitleSerializer(
            created_item,
            context=self.get_serializer_context())
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers)


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
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
