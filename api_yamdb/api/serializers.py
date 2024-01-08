from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import (RegexValidator,
                                    MaxValueValidator,
                                    MinValueValidator)
from django.shortcuts import get_object_or_404
from django.utils import timezone

from reviews.models import (Category,
                            Genre,
                            Title,
                            Review,
                            Comment,
                            User)


class UserEditSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        max_length=150, regex=r'^[\w.@+-]+\Z', required=True
    )
    email = serializers.EmailField(max_length=150, required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        read_only_fields = ('role',)


class TokenSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150, regex=r'^[\w.@+-]+\Z', required=True
    )
    confirmation_code = serializers.CharField(required=True)


class RegistrationSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150, regex=r'^[\w.@+-]+\Z', required=True
    )
    email = serializers.EmailField(max_length=254, required=True)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Username "me" запрещён к использованию'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id', )
        model = Category
        lookup_field = 'slug'


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
            RegexValidator(regex=r'^[\w.@+-]+\Z'),
        ]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('name', 'slug')
        model = Genre

    class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = (
                'name',
                'slug',
            )


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(
        required=True,
        many=True
    )
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'rating', 'genre', 'category'
        )
        read_only_fields = fields


class TitleSerializerWrite(serializers.ModelSerializer):
    year = serializers.IntegerField(
        required=True,
        validators=[
            MinValueValidator(
                0,
                'Нельзя добавлять произведения с годом меньше 0.'
            ),
            MaxValueValidator(
                timezone.now().year,
                'Нельзя добавлять произведения, которые еще не вышли.'
            ),
        ],
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        if Review.objects.filter(
            author=self.context['request'].user,
            title=get_object_or_404(
                Title,
                id=self.context['view'].kwargs.get('title_id'))
        ).exists():
            raise serializers.ValidationError(
                'Вы не можете добавить более'
                'одного отзыва на произведение')
        return data

    class Meta:
        model = Review
        fields = ('id',
                  'title',
                  'text',
                  'author',
                  'score',
                  'pub_date')
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment"""

    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')
