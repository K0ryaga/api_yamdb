from django.urls import include, path
from rest_framework import routers

from .views import UserRegistrationViewSet, ObtainTokenView

router = routers.DefaultRouter()
router.register(
    r'api/v1/auth/signup',
    UserRegistrationViewSet,
    basename='user-registration')

urlpatterns = [
    path('', include(router.urls)),
    path('api/v1/auth/token/',
         ObtainTokenView.as_view(),
         name='token_obtain_pair'),
]
