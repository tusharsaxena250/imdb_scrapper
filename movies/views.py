from rest_framework import generics
from .models import Movie
from .serializers import MovieSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = {
        'genre': ['exact', 'contains'],
        'release_year': ['exact', 'gte', 'lte'],
        'imdb_rating': ['exact', 'gte', 'lte'],
        'title': ['exact', 'contains'],
        'directors': ['exact', 'contains'],
        'cast': ['exact', 'contains'],
    }
    search_fields = ['title', 'plot_summary', 'directors', 'cast']

class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer