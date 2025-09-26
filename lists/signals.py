from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AnimeList

@receiver([post_save, post_delete], sender=AnimeList)
def update_stats(sender, instance, **kwargs):
    user = instance.user

    entries = user.anime.entries.all()
    user.profile.animeCount = entries.count()
    user.profile.episodesWatched = sum(entry.episodes_watched for entry in entries)
    user.profile.save()