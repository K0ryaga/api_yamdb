from rest_framework import serializers

from .models import (Category,
                     Genre,
                     Title,
                     Review,
                     Comment)
from api_yamdb.settings import MAX_SCORE, MIN_SCORE


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'slug',
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'name',
            'slug',
        )


class TitleSerializer(serializers.ModelSerializer):

    category = CategorySerializer(many=False, read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializerWrite(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        read_only=False,
        queryset=Category.objects.all(),
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        read_only=False,
        queryset=Genre.objects.all(),
        many=True,
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )
    score = serializers.IntegerField(
        min_value=MIN_SCORE, max_value=MAX_SCORE
    )

    def validate(self, data):
        if self.context['request'].method == 'POST':
            if Review.objects.filter(
                author=self.context['request'].user,
                title=self.context['view'].kwargs.get('title_id')
            ).exists():
                raise serializers.ValidationError(
                    'Нельзя оставить отзыв на одно произведение дважды'
                )
        return data

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment"""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'pub_date']
        read_only_fields = ['id', 'author', 'pub_date']
