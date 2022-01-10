from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр коментриев, только parents"""
    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсии children"""

    def to_representation(self, value):

        serializer = ReviewSerializer(value, context=self.context)
        return serializer.data


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод всех актеров и режиссеров"""
    class Meta:
        model = Actor
        fields = ('id', 'name', 'image',)


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод детального описания актеров или режиссеров"""
    class Meta:
        model = Actor
        fields = '__all__'


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'tagline', 'category', 'rating_user', 'middle_star')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзывов"""

    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзывов"""

    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ('name', 'text', 'children')


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полные фильмы"""
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft', )


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользывателям"""
    class Meta:
        model = Rating
        fields = ('star', 'movie')

    def create(self, validated_data):
        rating = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={'star': validated_data.get('star')}
        )

        return rating

