# movie_app/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
import secrets

# 3.party
from slugify import slugify
from autoslug import AutoSlugField



# Create your models here.

class Genre(models.Model):
    title = models.TextField()
    slug = AutoSlugField(populate_from='title', unique=True, slugify=slugify)
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Title: {self.title}"
    
    def get_absolute_url(self):
        return reverse('movie_app:category_detail_view', args=(self.slug,))

class Movie(models.Model):
    movie_id = models.IntegerField()
    title = models.TextField()
    slug = AutoSlugField(populate_from='title', unique=True, slugify=slugify)
    is_active = models.BooleanField(default=True)
    overview = models.TextField()
    genre = models.ManyToManyField(Genre)
    popularity = models.FloatField()
    poster = models.URLField(null=True, blank=True) # I dont want to store all 10.000 images locally. Due to that i prefer to store URL and send request for every image. Ideally its better to store locally.
    video = models.URLField(null=True, blank=True)
    release_date = models.DateField()
    language = models.TextField(max_length=100, null=True, blank=True)
    vote_average = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"Movie Title: {self.title}"
    
    def get_absolute_url(self):
        return reverse('movie_app:movie_detail_view', kwargs={'movie_slug':self.slug})
    
    @property
    def is_released(self):
        """Check if movie is released based on release_date"""
        from datetime import date
        return self.release_date <= date.today()
    
    class Meta:
        ordering = ("-release_date",)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment: {self.comment}"
    
    class Meta:
        ordering = ('-created_at',)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    slug = AutoSlugField(populate_from='get_username', unique=True, slugify=slugify)
    is_active = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='user-avatars/', default='default-avatar/default-avatar.webp')
    info = models.TextField()
    instagram = models.CharField(max_length=1024, null=True, blank=True)
    twitter = models.CharField(max_length=1024, null=True, blank=True)

    def get_username(self):
        return f"{self.user.username}"    

    def __str__(self):
        return f"{self.user.username}"
    
    def get_absolute_url(self):
        return reverse('movie_app:profile_detail_view', kwargs={'profile_slug':self.slug})


# Movie Night Models

class MovieNight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    access_code = models.CharField(max_length=32, unique=True, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.access_code:
            self.access_code = secrets.token_urlsafe(16)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Movie Night: {self.title}"
    
    def get_absolute_url(self):
        return reverse('movie_app:movie_night_detail', kwargs={'night_id': str(self.id)})
    
    class Meta:
        ordering = ['-created_at']


class MovieSuggestion(models.Model):
    movie_night = models.ForeignKey(MovieNight, on_delete=models.CASCADE, related_name='suggestions')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    suggested_by = models.CharField(max_length=100)  # Display name, not Django user
    created_at = models.DateTimeField(auto_now_add=True)
    is_watched_by_group = models.BooleanField(default=False)
    watched_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.movie.title} - suggested by {self.suggested_by}"
    
    def get_like_count(self):
        return self.likes.count()
    
    def get_seen_count(self):
        return self.user_interactions.filter(has_seen=True).count()
    
    def get_user_interaction(self, user_name):
        """Get interaction for a specific user name"""
        try:
            return self.user_interactions.get(user_name__iexact=user_name)
        except UserInteraction.DoesNotExist:
            return None
    
    def user_has_liked(self, user_name):
        interaction = self.get_user_interaction(user_name)
        return interaction.has_liked if interaction else False
    
    def user_has_seen(self, user_name):
        interaction = self.get_user_interaction(user_name)
        return interaction.has_seen if interaction else False
    
    def get_users_who_have_seen(self):
        """Get list of user names who have marked this as seen"""
        return list(self.user_interactions.filter(has_seen=True).values_list('user_name', flat=True))
    
    class Meta:
        unique_together = ['movie_night', 'movie']
        ordering = ['-created_at']


class UserInteraction(models.Model):
    suggestion = models.ForeignKey(MovieSuggestion, on_delete=models.CASCADE, related_name='user_interactions')
    user_name = models.CharField(max_length=100)  # Display name stored in browser
    has_liked = models.BooleanField(default=False)
    has_seen = models.BooleanField(default=False)
    has_liked_date = models.DateTimeField(null=True, blank=True)
    has_seen_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        from django.utils import timezone
        
        # Set dates when status changes to True, clear when False
        if self.has_liked and not self.has_liked_date:
            self.has_liked_date = timezone.now()
        elif not self.has_liked:
            self.has_liked_date = None
            
        if self.has_seen and not self.has_seen_date:
            self.has_seen_date = timezone.now()
        elif not self.has_seen:
            self.has_seen_date = None
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user_name} - {self.suggestion.movie.title}"
    
    class Meta:
        unique_together = ['suggestion', 'user_name']


class Like(models.Model):
    suggestion = models.ForeignKey(MovieSuggestion, on_delete=models.CASCADE, related_name='likes')
    user_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user_name} likes {self.suggestion.movie.title}"
    
    class Meta:
        unique_together = ['suggestion', 'user_name']
