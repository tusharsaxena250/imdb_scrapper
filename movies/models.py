from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=255)
    release_year = models.IntegerField(null=True, blank=True)
    imdb_rating = models.FloatField(null=True, blank=True)
    plot_summary = models.TextField(blank=True)
    directors = models.TextField(blank=True)  # Comma-separated director names
    cast = models.TextField(blank=True)      # Comma-separated actor names
    genre = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ['title', 'release_year']

    def __str__(self):
        return f"{self.title} ({self.release_year})"