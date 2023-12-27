from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator

from reviews.models import Category, Genre, User


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


class RegistrationSerializer(serializers.Serializer):
    username = serializers.RegexField(
        max_length=150, regex=r'^[\w.@+-]+\Z', required=True
    )
    email = serializers.EmailField(max_length=150, required=True)

    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Username "me" запрещён к использованию'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        if Category.objects.filter(slug=validated_data['slug']).exists():
            raise serializers.ValidationError(
                'Категория с таким слагом уже существует.')
        return super().create(validated_data)

    class Meta:
        model = Category
        exclude = ('id',)
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
    """Сериализатор для жанра."""

    def destroy(self, instance):
        instance.delete()

    class Meta:
        fields = ("name", "slug")
        model = Genre
