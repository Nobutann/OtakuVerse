from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from datetime import date

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    bio = models.TextField(max_length=500, blank=True)
    birthDate = models.DateField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')

    isPublic = models.BooleanField(default=True)
    showStats = models.BooleanField(default=True)

    animeCount = models.PositiveIntegerField(default=0)
    episodesWatched = models.PositiveIntegerField(default=0)

    joinedDate = models.DateTimeField(auto_now_add=True)
    lastOnline = models.DateTimeField(auto_now=True)

    FEMALE = 'F'
    MALE = 'M'
    CUSTOM = 'CUSTOM'
    NONE = 'NONE'

    GENDER = [
        (FEMALE, "Feminino"),
        (MALE, "Masculino"),
        (CUSTOM, "Customizado"),
        (NONE, "Prefiro não dizer"),
    ]

    gender = models.CharField(max_length=20, choices=GENDER, default=NONE)
    custom_gender = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def _resizeAvatar(self):
        try:
            img = Image.open(self.avatar.path)
            if img.height > 300 or img.width > 300:
                outputSize = (300, 300)
                img.thumbnail(outputSize, Image.Resampling.LANCZOS)
                img.save(self.avatar.path, quality=95)
        except Exception:
            pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.avatar and hasattr(self.avatar, 'path'):
            self._resizeAvatar()

@property
def age(self):
    if not self.birthDate:
        return None
    today = date.today()

    return today.year - self.birthDate.year() - ((today.month, today.day) < (self.birthDate.month, self.birthDate.day))

class FriendRequest(models.Model):
    STATUS = [
        ('pending', 'Pendente'),
        ('accepted', 'Aceitado'),
        ('rejected', 'Rejeitado'),
    ]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')