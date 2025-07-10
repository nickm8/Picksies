from django.contrib import admin
from .models import Movie, Genre, Profile, MovieNight, MovieSuggestion, UserInteraction, Like

# Register your models here.

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', "release_date", 'movie_id', 'is_released']
    list_filter = ['is_active', 'release_date', 'language']
    search_fields = ['title', 'movie_id']
    readonly_fields = ['slug']

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    readonly_fields = ['slug']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "slug", "info"]
    readonly_fields = ['slug']

@admin.register(MovieNight)
class MovieNightAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'access_code', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('created_by')

@admin.register(MovieSuggestion)
class MovieSuggestionAdmin(admin.ModelAdmin):
    list_display = ['movie', 'suggested_by', 'movie_night', 'is_watched_by_group', 'created_at']
    list_filter = ['is_watched_by_group', 'created_at', 'watched_date']
    search_fields = ['movie__title', 'suggested_by', 'movie_night__title']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('movie', 'movie_night')

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'suggestion', 'has_liked', 'has_seen']
    list_filter = ['has_liked', 'has_seen', 'created_at']
    search_fields = ['user_name', 'suggestion__movie__title']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('suggestion__movie')

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'suggestion', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user_name', 'suggestion__movie__title']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('suggestion__movie')
