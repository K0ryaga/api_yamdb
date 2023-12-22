from rest_framework import serializers
from django.contrib.auth.models import User


class RegistrationSerializer(serializers.Serializer):
    def validate_username(self, value):
        if value.lower() == 'me':
            raise serializers.ValidationError("Имя пользователя не может быть 'me'.")
        return value

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Этот email уже занят.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Это имя пользователя уже занято.")
        return attrs

    class Meta:
        model = User
        fields = ['email', 'username', 'confirmation_code']
