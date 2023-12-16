from django.urls import path
from .views import UserSignupViewSet, UserSignupByAdminViewSet

urlpatterns = [
    path('auth/signup/', UserSignupViewSet.as_view({'post': 'create'})),
    path('users/', UserSignupByAdminViewSet.as_view({'post': 'create'}))
]
