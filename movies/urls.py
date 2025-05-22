# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from .views import *

# router = DefaultRouter()
# router.register(r'movies', MovieViewSet)

# urlpatterns = [
#     path('', include(router.urls)),
#     path('scrape/', scrape_movies_view, name='scrape-movies'),
# ]
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('movies/', views.MovieListView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail'),
]