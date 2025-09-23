from django.db import models
from django.contrib.auth.models import User

class Anime(models.Model):
    mal_id = models.PositiveIntegerField(unique=True)
    title = models.CharField(max_length=300)
    title_english = models.CharField(max_length=300, blank=True, null=True)
    synopsis = models.TextField(blank=True, null=True)
    image_url = models.URLField()
    episodes = models.PositiveIntegerField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=50, blank=True)
    anime_type = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=50, blank=True)
    studios = models.CharField(max_length=300, blank=True)
    genres = models.CharField(max_length=500, blank=True)

    def __str__(self):
        return self.title