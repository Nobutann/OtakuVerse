from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView, DetailView

from .forms import RatingForm
from .models import Anime, Rating

def _ensure_session(request: HttpRequest) -> str:
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key

class AnimeListView(ListView):
    model = Anime
    template_name = "reviews/anime_list.html"
    context_object_name = "animes"

    def get_queryset(self):
        return (
            Anime.objects.all()
            .annotate(media=Avg("ratings__nota"), qtd=Count("ratings"))
        )

class AnimeDetailView(DetailView):
    model = Anime
    template_name = "reviews/anime_detail.html"
    context_object_name = "anime"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        anime: Anime = ctx["anime"]
        session_key = _ensure_session(self.request)

        avaliacao = Rating.objects.filter(anime=anime, session_key=session_key).first()
        if avaliacao:
            form = RatingForm(initial={"nota": avaliacao.nota, "comentario": avaliacao.comentario})
        else:
            form = RatingForm()

        ctx.update({
            "form": form,
            "media": anime.media,
            "qtd": anime.total_avaliacoes,
            "minhas_estrelas": avaliacao.nota if avaliacao else 0,
            "avaliacoes": anime.ratings.select_related("anime")[:20],
        })
        return ctx

def rate_anime(request: HttpRequest, pk: int) -> HttpResponse:
    anime = get_object_or_404(Anime, pk=pk)
    session_key = _ensure_session(request)

    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            nota = form.cleaned_data["nota"]
            comentario = form.cleaned_data["comentario"]
            Rating.objects.update_or_create(
                anime=anime,
                session_key=session_key,
                defaults={"nota": nota, "comentario": comentario},
            )
            return redirect(reverse("anime_detail", kwargs={"pk": anime.pk}))
    else:
        form = RatingForm()

    return render(request, "reviews/rate_anime.html", {"anime": anime, "form": form})