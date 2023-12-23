from django.urls import include, path
from rest_framework import routers

from .views import (
    RegistrationViewSet,
    TokenObtainView,
    CategoryViewSet,
    UserViewSet,
    GenreViewSet,
)
from reviews.views import (
                           TitleViewSet,
                           ReviewViewSet,
                           CommentViewSet,)


router = routers.DefaultRouter()
router.register(
    r'v1/auth/signup',
    RegistrationViewSet,
    basename='user-registration'
)
router.register(
    r'v1/categories',
    CategoryViewSet,
    basename='category'
)
router.register(
    r'v1/genres',
    GenreViewSet,
    basename='genre'
)
router.register(r'v1/titles', TitleViewSet, basename='title')
router.register(
    r'v1/titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='review')
router.register(
    r'v1/titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comment'
)
router.register(
    r'v1/users',
    UserViewSet,
    basename='user'
)


urlpatterns = [
    path('api/', include(router.urls)),
    path('v1/auth/token/', TokenObtainView.as_view(), name='token_obtain_pair'),
]
