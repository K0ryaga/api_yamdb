from datetime import datetime

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from .models import (Category,
                     Genre,
                     Title,
                     Review,
                     Comment)


class TitleSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        current_year = datetime.now().year
        release_year = validated_data.get('year')
        if release_year and release_year > current_year:
            raise serializers.ValidationError("Invalid release year")

        genre_data = validated_data.pop('genre')
        category_data = validated_data.pop('category')

        genre = Genre.objects.get(id=genre_data['id'])
        category = Category.objects.get(id=category_data['id'])

        title = Title.objects.create(
            genre=genre,
            category=category,
            **validated_data
        )
        return title

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'description', 'genre', 'category']


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
        if self.context['request'].user.is_staff or self.context['request'].user == instance.user:
            instance.delete()
        else:
            raise serializers.ValidationError('У вас нет прав для удаления отзыва.')

    class Meta:
        model = Review
        fields = ['id', 'title', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class CommentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def get_queryset(self):
        review_id = self.context['view'].kwargs['review_id']
        return Comment.objects.filter(review_id=review_id)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if not (user == instance.author or user.is_staff):
            raise PermissionDenied("У вас нет прав для редактирования комментария.")
        return super().update(instance, validated_data)

    def delete(self):
        user = self.context['request'].user
        if not (user == self.instance.author or user.is_staff):
            raise PermissionDenied("У вас нет прав для удаления комментария.")
        self.instance.delete()

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'pub_date']
        read_only_fields = ['id', 'author', 'pub_date']
