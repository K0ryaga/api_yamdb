from django.urls import include, path
from rest_framework import routers
from api.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'titles/(?P<title_id>\d+)/reviews',
                ReviewViewSet,
                basename='review')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
