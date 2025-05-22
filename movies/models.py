# from django.db import models

# class Movie(models.Model):
#     title = models.CharField(max_length=255)
#     release_year = models.IntegerField(null=True, blank=True)
#     imdb_rating = models.FloatField(null=True, blank=True)
#     plot_summary = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('title', 'release_year')

#     def __str__(self):
#         return self.title

# class Person(models.Model):
#     name = models.CharField(max_length=255, unique=True)

#     def __str__(self):
#         return self.name

# class MoviePerson(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='persons')
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     role = models.CharField(max_length=50)  # e.g., 'Director', 'Actor'

#     class Meta:
#         unique_together = ('movie', 'person', 'role')

#     def __str__(self):
#         return f"{self.person.name} as {self.role} in {self.movie.title}"

from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_year = models.IntegerField(null=True, blank=True)
    imdb_rating = models.FloatField(null=True, blank=True)
    plot_summary = models.TextField(blank=True)
    directors = models.TextField(blank=True)  # Comma-separated director names
    cast = models.TextField(blank=True)      # Comma-separated actor names
    genre = models.CharField(max_length=100, blank=True)

    class Meta:
        unique_together = ['title', 'release_year']

    def __str__(self):
        return f"{self.title} ({self.release_year})"