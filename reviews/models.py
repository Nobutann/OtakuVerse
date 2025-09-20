from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg

class Anime(models.Model):
    titulo = models.CharField(max_length=200, unique=True)
    sinopse = models.TextField(blank=True)
    capa_url = models.URLField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["titulo"]

    def __str__(self) -> str:
        return self.titulo

    @property
    def media(self) -> float:
        return self.ratings.aggregate(avg=Avg("nota"))["avg"] or 0.0

    @property
    def total_avaliacoes(self) -> int:
        return self.ratings.count()

class RatingQuerySet(models.QuerySet):
    def aggregate_avg(self) -> float:
        return self.aggregate(avg=Avg("nota"))["avg"] or 0.0

class Rating(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="ratings")
    session_key = models.CharField(max_length=40)  # identifica usuário anônimo
    nota = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = RatingQuerySet.as_manager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["anime", "session_key"], name="unique_rating_per_session_per_anime")
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.anime.titulo} - {self.nota}★"