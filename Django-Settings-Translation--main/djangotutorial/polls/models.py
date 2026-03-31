import datetime

from django.contrib import admin
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=50, default="#3b82f6")

    def __str__(self):
        return self.name

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    end_date = models.DateTimeField("date ends", null=True, blank=True)

    def __str__(self):
        return self.question_text

    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_active(self):
        now = timezone.now()
        if self.end_date and now > self.end_date:
            return False
        return True

    def get_recent_voter_count(self):
        # 24 saat içindeki oy sayısını getir
        last_24h = timezone.now() - datetime.timedelta(days=1)
        return self.votes.filter(vote_date__gte=last_24h).count()

class Comment(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.question.id}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.points} Puan"
    
    @property
    def rank(self):
        if self.points < 50:
            return "Bronz Üye"
        elif self.points < 200:
            return "Gümüş Üye"
        elif self.points < 500:
            return "Altın Üye"
        else:
            return "Platin Üye"

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Emoji or SVG name")
    points_threshold = models.IntegerField(default=0, help_text="Points needed to earn this badge")

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    image = models.ImageField("Seçenek Görseli", upload_to='choices/', blank=True, null=True)

    def __str__(self):
        return self.choice_text

class ChatMessage(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}"

class VoterIP(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    vote_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'ip_address')

class Reaction(models.Model):
    REACTION_CHOICES = [
        ('HEART', '❤️'),
        ('FIRE', '🔥'),
        ('THINK', '🤔'),
        ('WOW', '😮'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user', 'emoji')

# Signals to auto-create Profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)
