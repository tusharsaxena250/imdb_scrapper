from django.test import TestCase
from movies.serializers import MovieSerializer

class MovieSerializerTest(TestCase):
    def test_serializer_valid_data(self):
        data = {
            'title': 'Virgin Territory',
            'release_year': 2007,
            'imdb_rating': 4.7,
            'plot_summary': 'Young Florentines take refuge...',
            'directors': 'David Leland',
            'cast': 'Hayden Christensen,Mischa Barton'
        }
        serializer = MovieSerializer(data=data)
        self.assertTrue(serializer.is_valid(), msg=serializer.errors)
        self.assertEqual(serializer.validated_data, data)

    def test_serializer_invalid_rating(self):
        data = {
            'title': 'Virgin Territory',
            'release_year': 2007,
            'imdb_rating': 11.0,
            'plot_summary': 'Young Florentines...',
            'directors': 'David Leland',
            'cast': 'Hayden Christensen,Mischa Barton'
        }
        serializer = MovieSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('imdb_rating', serializer.errors)

    def test_serializer_invalid_title(self):
        data = {
            'title': 'Invalid@Title#',
            'release_year': 2007,
            'imdb_rating': 4.7,
            'plot_summary': 'Young Florentines...',
            'directors': 'David Leland',
            'cast': 'Hayden Christensen,Mischa Barton'
        }
        serializer = MovieSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)