from django.contrib import admin
from django.urls import path

# views
from . import views

app_name = "movie_app"

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("movie/<slug:movie_slug>/", views.movie_detail_view, name="movie_detail_view"),
    path("category/<slug:category_slug>/", views.category_view, name="category_detail_view"),
    path("most-popular-movies/", views.most_popular_movies_view, name="most_popular_movies"),
    path('account/delete-account/', views.delete_account_view, name="delete_account_view"),
    path('account/change-password/', views.change_password_view, name='change_password'),
    path('account/update-profile/', views.update_profile_view, name="update_profile_view" ),
    path('account/<slug:profile_slug>/', views.profile_detail_view, name='profile_detail_view'),
    path('login/', views.login_view, name="login"),
    path("signup/", views.signup_View, name='signup'),
    path('logout/', views.logout_view, name="logout"),
    path('s', views.search, name="search"),
    path('health/', views.health_check, name="health_check"),
    
    # Movie Night URLs
    path('create-movie-night/', views.create_movie_night, name='create_movie_night'),
    path('nights/<uuid:night_id>/', views.movie_night_detail, name='movie_night_detail'),
    path('nights/<uuid:night_id>/suggest/', views.add_movie_suggestion, name='add_movie_suggestion'),
    path('nights/<uuid:night_id>/suggestions/<int:suggestion_id>/like/', views.toggle_like, name='toggle_like'),
    path('nights/<uuid:night_id>/suggestions/<int:suggestion_id>/seen/', views.toggle_seen, name='toggle_seen'),
    path('nights/<uuid:night_id>/suggestions/<int:suggestion_id>/watched/', views.mark_watched_by_group, name='mark_watched_by_group'),
    path('nights/<uuid:night_id>/suggestions/<int:suggestion_id>/delete/', views.delete_suggestion, name='delete_suggestion'),
    
    # Random movie picker endpoint
    path('nights/<uuid:night_id>/random-pick/', views.random_movie_pick, name='random_movie_pick'),
    
    # TMDB API endpoints
    path('api/search-movies/', views.search_tmdb_movies, name='search_tmdb_movies'),
    path('api/add-tmdb-movie/', views.add_tmdb_movie_to_db, name='add_tmdb_movie_to_db'),
]
