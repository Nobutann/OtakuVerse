from django.db import models
from django.db.models import Avg

class Anime(models.Model):

    def media_notas(self):
        from reviews.models import Review
        media = Review.objects.filter(anime=self).aggregate(avg=Avg('rating'))['avg']
        return round(media, 1) if media else None

