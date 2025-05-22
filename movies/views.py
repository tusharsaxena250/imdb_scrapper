# from rest_framework import viewsets
# from .models import Movie
# from .serializers import MovieSerializer

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from .scraper import scrape_movies

# class MovieViewSet(viewsets.ModelViewSet):
#     queryset = Movie.objects.all()
#     serializer_class = MovieSerializer

# @api_view(['POST', 'GET'])
# def scrape_movies_view(request):
#     keyword = request.query_params.get('keyword')
#     if not keyword:
#         return Response({'error': 'Keyword parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         limit = int(request.query_params.get('limit', 50))
#         offset = int(request.query_params.get('offset', 0))
#     except ValueError:
#         return Response({'error': 'Limit and offset must be integers'}, status=status.HTTP_400_BAD_REQUEST)

#     movies = scrape_movies(keyword, limit=limit, offset=offset)
#     print('movies: ', movies)
#     return Response({
#     'message': f"Scraped {len(movies)} movies for keyword '{keyword}' with limit={limit} and offset={offset}",
#     'data': [
#         {
#             'title': movie.title,
#             'year': movie.year,
#             'rating': movie.rating,
#             'directors': movie.directors,
#             'cast': movie.cast,
#             'summary': movie.summary,
#         }
#         for movie in movies
#     ]
# })

# from rest_framework import viewsets
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import Movie
# from .serializers import MovieSerializer
# from .scraper import scrape_imdb

# class MovieViewSet(viewsets.ModelViewSet):
#     queryset = Movie.objects.all()
#     serializer_class = MovieSerializer

# @api_view(['POST'])
# def scrape_movies(request):
#     genre = request.data.get('genre', 'comedy')
#     max_pages = request.data.get('max_pages', 2)
#     try:
#         scrape_imdb(genre, max_pages=int(max_pages))
#         return Response({"status": "Scraping completed", "genre": genre, "pages_scraped": max_pages})
#     except Exception as e:
#         return Response({"status": "Error", "message": str(e)}, status=500)

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