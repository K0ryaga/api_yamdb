from django.urls import include, path
from rest_framework import routers
from .views import sign_up
from .views import (
    TokenApiView,
    CategoryViewSet,
    UsersViewSet,
    GenreViewSet,
    TitleViewSet,
    ReviewViewSet,
    CommentViewSet
)

v1_router = routers.DefaultRouter()
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='category'
)
v1_router.register(
    'genres',
    GenreViewSet,
    basename='genre'
)
v1_router.register('titles', TitleViewSet, basename='title')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
v1_router.register(
    'users',
    UsersViewSet,
    basename='users'
)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/token/', TokenApiView.as_view(), name='token_obtain_pair'),
    path('v1/auth/signup/', sign_up, name='signup'),
]
