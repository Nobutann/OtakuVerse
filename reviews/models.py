from django.db import models
from django.contrib.auth.models import User

SCORE_CHOICES = [
    (10, "10 - Obra-Prima"),
    (9, "9 - Ótimo"),
    (8, "8 - Muito Bom"),
    (7, "7 - Bom"),
    (6, "6 - Aceitável"),
    (5, "5 - Mediano"),
    (4, "4 - Ruim"),
    (3, "3 - Muito Ruim"),
    (2, "2 - Horrível"),
    (1, "1 - Terrível"),
]

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    anime_id = models.IntegerField()
    score = models.IntegerField(choices=SCORE_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'anime_id')

    def __str__(self):
        return f"{self.user} - {self.anime_id} ({self.score})"
