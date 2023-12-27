from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from django.core.validators import RegexValidator
from .utils import generate_confirmation_code, send_confirmation_email
from reviews.models import Category, Genre, User
from reviews.constants import (
    EMAIL_MAX_LEN, USERNAME_MAX_LEN
)

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
            raise serializers.ValidationError('Категория с таким слагом уже существует.')
        return super().create(validated_data)

    def delete(self, instance):
        if not self.context['request'].user.is_staff:
            raise exceptions.PermissionDenied('У вас нет прав для удаления категории.')
        instance.delete()
        return None

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        extra_kwargs = {
            'slug': {'validators': []},
        }


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

    def create(self, validated_data):
        genre = Genre.objects.create(**validated_data)
        self.instance = genre
        return genre

    def destroy(self, instance):
        instance.delete()

    class Meta:
        fields = ("name", "slug")
        model = Genre
        extra_kwargs = {
            'slug': {'validators': []}
        }