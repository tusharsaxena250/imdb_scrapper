from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('movies/', views.MovieListView.as_view(), name='movie-list'),
    path('movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail'),
]