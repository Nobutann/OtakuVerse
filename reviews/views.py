from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from animes.models import Anime
from .models import Review

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

@login_required
def avaliar_anime(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)
    user_review = Review.objects.filter(anime_id=anime_id, user=request.user).first()

    if request.method == 'POST':
        score = int(request.POST.get('score'))
        comment = request.POST.get('comment', '').strip()

        if user_review:
            user_review.score = score
            user_review.comment = comment
            user_review.save()
        else:
            Review.objects.create(
                anime_id=anime_id,
                user=request.user,
                score=score,
                comment=comment
            )

        return redirect('detalhes_anime', anime_id=anime.id)
    
    return redirect('detalhes_anime', anime_id=anime.id)
