# api/serializers.py
from rest_framework import serializers
from reviews.models import Review, Title


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
