from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанра."""

    class Meta:
        fields = ("name", "slug")
        model = Genre
        lookup_field = "slug"


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категории."""

    class Meta:
        fields = ("name", "slug")
        model = Category
        lookup_field = "slug"



class TitleRetrieveSerializer(serializers.ModelSerializer):
    """Сериализатор для показа произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            "id",
            "name",
            "year",
            "rating",
            "description",
            "genre",
            "category",
        )
        model = Title

    def get_rating(self, obj):
        obj = obj.reviews.all().aggregate(rating=Avg("score"))
        return obj["rating"]


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания произведений."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field="slug"
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field="slug", many=True
    )

    class Meta:
        fields = ("id", "name", "description", "year", "category", "genre")
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        title_id = self.context['view'].kwargs['title_id']
        user = self.context['request'].user
        title = Title.objects.get(id=title_id)

        existing_review = Review.objects.filter(title=title, user=user).exists()
        if existing_review:
            raise serializers.ValidationError('Вы уже оставляли отзыв')

        validated_data['title'] = title
        validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.rating = validated_data.get('rating', instance.rating)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance

    def validate_id(self, value):
        title_id = self.context['view'].kwargs['title_id']
        try:
            Review.objects.get(id=value, title_id=title_id)
        except Review.DoesNotExist:
            raise serializers.ValidationError('Отзыв не найден')
        return value

    def delete(self, instance):
        instance.delete()

    class Meta:
        model = Review
        fields = ['id', 'title', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        
        
class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели комментария."""

    author = serializers.SlugRelatedField(
        slug_field="username",
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ("id", "author", "review", "text", "pub_date")
        read_only_fields = ("review",)
        model = Comment
