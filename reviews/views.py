from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from animes.models import Anime
from .forms import ReviewForm
from .models import Review

@login_required
def avaliar_anime(request, anime_id):
    anime = get_object_or_404(Anime, id=anime_id)

    existing_review = Review.objects.filter(anime_id=anime_id, user=request.user).first()

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.anime_id = anime_id
            review.user = request.user
            review.save()
            return redirect("detalhes_anime", anime_id=anime.id)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, "reviews/add_review.html", {"form": form, "anime": anime})
