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
    
class AnimeList(models.Model):
    STATUS = [
        ('watching', 'Assistindo'),
        ('completed', 'Completo'),
        ('ptw', 'Planejo Assistir'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='anime_entries')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='user_entries')
    score = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='ptw')
    episodes_watched = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'anime']

    def __str__(self):
        return f"{self.user.username} - {self.anime.title} ({self.status})"

class FavoriteCharacter(models.Model):
    """Guarda um personagem favorito para um usuário específico."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mal_id = models.IntegerField()
    name = models.CharField(max_length=255)
    image_url = models.URLField()

    class Meta:
        unique_together = ('user', 'mal_id')

    def __str__(self):
        return f"{self.name} (Favorito de {self.user.username})"