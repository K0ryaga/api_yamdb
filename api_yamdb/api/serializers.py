from rest_framework import serializers, exceptions
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from .utils import generate_confirmation_code, send_confirmation_email
from reviews.models import Category, Genre


class RegistrationSerializer(serializers.Serializer):
    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Этот email уже занят.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Это имя пользователя уже занято.")
        confirmation_code = generate_confirmation_code()
        send_confirmation_email(email, confirmation_code)
        attrs['confirmation_code'] = confirmation_code
        return attrs

    class Meta:
        model = User
        fields = ['email', 'username', 'confirmation_code']


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
    def get_queryset(self):
        if not self.context['request'].user.is_superuser:
            raise PermissionDenied("доступ запрещен. Вы не являетесь администратором.")

        return super().get_queryset()

    def create(self, validated_data):
        if not self.context['request'].user.is_superuser:
            raise PermissionDenied("Доступ запрещен. Только администратор может создать пользователя.")

        last_name = validated_data.get('last_name')
        if len(last_name) > 150:
            raise serializers.ValidationError({"last_name": "Длина поля last_name не должна превышать 150 символов."})

        email = validated_data.get('email')
        username = validated_data.get('username')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Этот email уже занят."})
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Это имя пользователя уже занято."})

        user = User.objects.create_user(**validated_data)
        return user

    def validate_username(self, value):
        if not self.context['request'].user.is_superuser:
            raise PermissionDenied("Доступ запрещен. Только администратор может создать пользователя.")
        return value

    def update_by_admin(self, instance, validated_data):
        if not self.context['request'].user.is_superuser:
            raise PermissionDenied("Доступ запрещен. Только администратор может редактировать пользователя.")
        email = validated_data.get('email')
        username = validated_data.get('username')
        if User.objects.filter(email=email).exclude(username=instance.username).exists():
            raise serializers.ValidationError({"email": "Этот email уже занят."})
        if User.objects.filter(username=username).exclude(username=instance.username).exists():
            raise serializers.ValidationError({"username": "Это имя пользователя уже занято."})
        instance.email = email
        instance.username = username
        instance.save()
        return instance

    def delete(self, instance):
        if not self.context['request'].user.is_superuser:
            raise PermissionDenied("Доступ запрещен. Только администратор может удалить пользователя.")

    def retrieve(self, instance):
        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Доступ запрещен. Вы не авторизованы.")
        return instance

    def update_by_user(self, instance, validated_data):
        if not self.context['request'].user.is_authenticated:
            raise serializers.ValidationError("Доступ запрещен. Вы не авторизованы.")

        last_name = validated_data.get('last_name')
        if len(last_name) > 150:
            raise serializers.ValidationError({"last_name": "Длина поля last_name не должна превышать 150 символов."})

        email = validated_data.get('email')
        username = validated_data.get('username')
        if User.objects.filter(email=email).exclude(username=instance.username).exists():
            raise serializers.ValidationError({"email": "Этот email уже занят."})
        if User.objects.filter(username=username).exclude(username=instance.username).exists():
            raise serializers.ValidationError({"username": "Это имя пользователя уже занято."})

        instance.email = email
        instance.username = username
        instance.save()

        return instance

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True}}


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