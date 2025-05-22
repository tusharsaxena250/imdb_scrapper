# from rest_framework import serializers
# from .models import Movie

# class MovieSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Movie
#         fields = '__all__'
# from rest_framework import serializers
# from .models import Movie

# class MovieSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Movie
#         fields = ['id', 'title', 'release_year', 'rating', 'director', 'cast', 'plot_summary', 'genre', 'created_at']

# from rest_framework import serializers
# from .models import Movie

# class PersonSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Person
#         fields = ['name']

# class MoviePersonSerializer(serializers.ModelSerializer):
#     person = PersonSerializer()
#     role = serializers.CharField()

#     class Meta:
#         model = MoviePerson
#         fields = ['person', 'role']

# class MovieSerializer(serializers.ModelSerializer):
#     persons = MoviePersonSerializer(many=True, source='persons.all')

#     class Meta:
#         model = Movie
#         fields = ['id', 'title', 'release_year', 'imdb_rating', 'plot_summary', 'persons']

from rest_framework import serializers
from movies.models import Movie
import re

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'release_year', 'imdb_rating', 'plot_summary', 'directors', 'cast', 'genre']
        read_only_fields = ['id']
        extra_kwargs = {
            'title': {'required': True, 'allow_blank': False},
            'release_year': {'required': False, 'allow_null': True},
            'imdb_rating': {'required': False, 'allow_null': True},
            'plot_summary': {'required': False, 'allow_blank': True},
            'directors': {'required': False, 'allow_blank': True},
            'cast': {'required': False, 'allow_blank': True},
            'genre': {'required': False, 'allow_blank': True},
        }

    def validate_title(self, value):
        """Validate that the movie title contains only allowed characters."""
        if value and not re.match(r'^[a-zA-Z0-9\s\-\'\(\):,.!]+$', value):
            raise serializers.ValidationError("Title contains invalid characters.")
        return value

    def validate_imdb_rating(self, value):
        """Ensure imdb_rating is between 0 and 10 if provided."""
        if value is not None:
            if not isinstance(value, (int, float)):
                raise serializers.ValidationError("IMDb rating must be a number.")
            if not 0 <= value <= 10:
                raise serializers.ValidationError("IMDb rating must be between 0 and 10.")
        return value