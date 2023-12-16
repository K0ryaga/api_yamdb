from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from reviews.models import Review
from api.serializers import ReviewSerializer
from .permissions import IsReviewOwnerOrModeratorOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewOwnerOrModeratorOrAdmin]
    lookup_field = 'title_id'
