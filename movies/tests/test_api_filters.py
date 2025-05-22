from django.urls import reverse
from rest_framework.test import APITestCase
from movies.models import Movie

class MovieAPITest(APITestCase):
    def setUp(self):
        Movie.objects.create(
            title="Virgin Territory", release_year=2007, imdb_rating=4.7,
            plot_summary="Young Florentines...", directors="David Leland",
            cast="Hayden Christensen,Mischa Barton", genre="comedy"
        )
        Movie.objects.create(
            title="Future Movie", release_year=2025, imdb_rating=8.0,
            plot_summary="A futuristic tale...", directors="Jane Doe",
            cast="John Doe", genre="sci-fi"
        )

    def test_filter_by_genre(self):
        response = self.client.get(reverse('movies:movie-list') + '?genre=comedy')
        print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Virgin Territory")

    def test_filter_by_imdb_rating_gte(self):
        response = self.client.get(reverse('movies:movie-list') + '?imdb_rating__gte=7.0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Future Movie")

    def test_filter_by_title_contains(self):
        response = self.client.get(reverse('movies:movie-list') + '?title__contains=Virgin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Virgin Territory")

    def test_filter_by_release_year(self):
        response = self.client.get(reverse('movies:movie-list') + '?release_year=2025')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Future Movie")

    def test_search_by_title(self):
        response = self.client.get(reverse('movies:movie-list') + '?search=Virgin')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "Virgin Territory")