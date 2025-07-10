# movie_app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q, Case, When, IntegerField
from django.conf import settings

from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

# Python imports
import datetime
import random
import json
import requests
import os
import logging

# Models
from django.contrib.auth.models import User
from .models import Movie, Genre, Comments, Profile, MovieNight, MovieSuggestion, UserInteraction, Like
from .utils import generate_movie_night_token, verify_movie_night_token, movie_night_required

# Forms
from movie_app.forms import CommentForm, UserSignUpForm, UserLoginForm, ChangeUserPasswordForm, DeleteAccountForm, ProfileUpdateForm

logger = logging.getLogger(__name__)


# Views

def movie_nights_homepage(request):
    """Movie nights homepage using Vue.js"""
    return render(request, 'app.html', {
        'component_name': 'Welcome',
        'inertia_data': json.dumps({'message': 'Hello from Django + Vue.js!'})
    })

def simple_test(request):
    """Simple test view for Vue.js"""
    return render(request, 'app.html', {
        'component_name': 'Test',
        'inertia_data': json.dumps({'test': 'working from Django'})
    })

def homepage(request):
    # Redirect authenticated users to create_movie_night
    if request.user.is_authenticated:
        return redirect('movie_app:create_movie_night')
        
    return redirect('movie_app:create_movie_night')

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    popular_movies = Movie.objects.order_by('-popularity').filter(is_active=True)[:6] # Most popular 6 Movies
    latest_movies = Movie.objects.order_by('-release_date').filter(is_active=True)
    paginator = Paginator(latest_movies, 20)
    page_number = request.GET.get("page")
    last_movies = paginator.get_page(page_number,)
    context = dict(popular_movies=popular_movies, last_movies=last_movies)
    return render(request, 'movie_app/homepage.html', context=context)
        

def most_popular_movies_view(request):
    popular_movies = Movie.objects.order_by('-popularity').filter(is_active=True)
    paginator = Paginator(popular_movies, 20)
    page_number = request.GET.get("page")
    p_movies = paginator.get_page(page_number,)
    context = dict(popular_movies=p_movies, page_title='Most Popular Movies')
    return render(request, 'movie_app/most-popular-movies.html', context=context)


def category_view(request, category_slug):
    category = get_object_or_404(Genre,slug=category_slug, is_active=True)
    category_movies = Movie.objects.filter(genre=category)
    paginator = Paginator(category_movies,20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = dict(category=category,category_movies=page_obj, page_title=category.title )
    return render(request, 'movie_app/category-detail.html', context=context)


# Movie Detail

def movie_detail_view(request, movie_slug):
    movie = get_object_or_404(Movie,slug=movie_slug, is_active=True)
    form = CommentForm(request.POST or None)
    if request.user.is_authenticated:
        form.fields['user'].queryset = User.objects.filter(username=request.user.username)
    movie_comments = Comments.objects.filter(movie=movie)
    paginator = Paginator(movie_comments, 10)
    page_number = request.GET.get('page')
    paginated_page = paginator.get_page(page_number)
    context = dict(movie=movie, form=form, movie_comments=paginated_page)
    if form.is_valid():
        form = form.save(commit=False)
        form.user = request.user
        form.movie = movie
        form.save()
        messages.success(request, 'Your comment was successfully recorded')
        return redirect(reverse('movie_app:movie_detail_view', args=(movie.slug,)))
    return render(request, 'movie_app/movie-detail.html', context=context)


# Search ##

def search(request):    
    search_term = request.GET.get('search')
    if not search_term:
        return render(request, 'search.html', {'search_term': ''})
    
    # Search both local database and TMDB
    movie_items = Movie.objects.filter(
        Q(title__icontains=search_term) | Q(overview__icontains=search_term)
    ).select_related().prefetch_related('genre')
    
    paginator = Paginator(movie_items, 20)
    page_number = request.GET.get('page')
    obj = paginator.get_page(page_number)
    
    # Also search TMDB if we have API access
    tmdb_results = []
    api_key = getattr(settings, 'TMDB_API_KEY', '')
    
    if api_key and len(search_term) > 2:  # Only search TMDB for longer queries
        try:
            url = f'https://api.themoviedb.org/3/search/movie'
            params = {
                'api_key': api_key,
                'query': search_term,
                'language': 'en-US',
                'page': 1,
                'include_adult': False
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Filter out movies already in our database
                existing_ids = set(Movie.objects.values_list('movie_id', flat=True))
                
                for movie in data.get('results', [])[:5]:  # Limit to 5 TMDB results
                    if movie.get('id') not in existing_ids:
                        tmdb_results.append({
                            'id': movie.get('id'),
                            'title': movie.get('title'),
                            'overview': movie.get('overview', '')[:300] + ('...' if len(movie.get('overview', '')) > 300 else ''),
                            'release_date': movie.get('release_date'),
                            'poster_path': f"https://image.tmdb.org/t/p/w300{movie.get('poster_path')}" if movie.get('poster_path') else None,
                            'vote_average': movie.get('vote_average'),
                        })
        except:
            pass  # Fail silently if TMDB search fails
    
    context = {
        'search_movies': obj,
        'tmdb_results': tmdb_results,
        'search_term': search_term,
        'has_tmdb_api': bool(api_key)
    }
    return render(request, 'search.html', context=context)


# Authentication

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, f"Welcome {request.user.get_full_name()} You Already Logged in.")
        return redirect('/')
    form = UserLoginForm(request.POST or None)
    context = dict(form=form, page_title='Login')
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'{request.user.username} You are succesfully logged in.')
            return redirect('/')
        messages.warning(request, 'Wrong password or username. Please check the info and try again.')
        return render(request, 'registration/authentication.html', context=context)
    return render(request, 'registration/authentication.html', context=context)

# Signup
def signup_View(request):
    form = UserSignUpForm(request.POST or None)
    context = dict(form=form, page_title='Signup')
    if form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data.get('password'))
        user.save()
        Profile.objects.create(user=user)
        messages.success(request, 'Your Account/Profile is Succesfully Created.')
        return redirect(reverse('movie_app:login'))
    return render(request, 'registration/authentication.html', context)

# logout
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'You are logged out.')
        return redirect('/')
    else:
        if request.META.get('HTTP_REFERER'):
            return redirect(request.META['HTTP_REFERER'])
        else:
            return redirect('/')


# Change Password
@login_required(login_url='/login/')
def change_password_view(request):
        user = request.user
        form = ChangeUserPasswordForm(request.POST or None)
        if form.is_valid():
            password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data['new_password']
            if user.check_password(password): # this can be done in forms.py form validation but i prefer to make it on view level.
                user.set_password(new_password) # hashing string password data.
                user.save()
                messages.success(request, f'{user.username} your password changed succesfully.')
                return redirect(user.profile.get_absolute_url())
            messages.warning(request, 'Password is wrong. Please check and try again.')
            return redirect(reverse('movie_app:change_password'))
    
        context = dict(form=form, page_title=f'{user.username} Change Password')
        return render(request, 'registration/authentication.html', context=context)


# Delete Account
@login_required(login_url='/login/')
def delete_account_view(request):
    form = DeleteAccountForm(request.POST or None)
    if form.is_valid():
        if form.cleaned_data['number'] == request.session.get('confirmation_int'):
            user = request.user
            user.delete()
            messages.success(request, 'Your account has been deleted :(')
            return redirect('movie_app:signup')
        messages.warning(request, 'Wrong confirmation number. Please check and try again.')
        return redirect('movie_app:delete_account_view')
    confirmation_int = random.randint(1000000,15000000)
    request.session['confirmation_int'] = confirmation_int
    context = dict(form=form, confirmation_int=confirmation_int, page_title=f'{request.user.username} Account Delete')
    return render(request, 'registration/delete.html', context=context)

# PROFILE

# profile detail
def profile_detail_view(request, profile_slug):
    profile = get_object_or_404(Profile, slug=profile_slug, is_active=True)
    user_comments = profile.user.comments_set.all()
    paginator = Paginator(user_comments,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = dict(profile=profile, user_comments=page_obj)
    return render(request, 'movie_app/profile-detail.html', context=context )

# change profile info
@login_required(login_url='/login/')
def update_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user, is_active=True)
    form = ProfileUpdateForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, 'Your Profile Succesfully Updated')
        return redirect(profile.get_absolute_url())
    context = dict(form=form, page_title = f'{request.user.username} Profile Update')
    return render(request, 'registration/authentication.html', context=context)


# Health Check
@never_cache
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for Docker and load balancers"""
    try:
        # Basic database check
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check if we can access the models
        Movie.objects.count()
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'error': str(e)
        }, status=500)


# Movie Night Views

def create_movie_night(request):
    """Admin-only: Create a new movie night"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        
        movie_night = MovieNight.objects.create(
            title=title,
            description=description,
        )
        
        token = generate_movie_night_token(movie_night)
        share_url = request.build_absolute_uri(f'/nights/{movie_night.id}?t={token}')
        
        return JsonResponse({
            'success': True,
            'movie_night_id': str(movie_night.id),
            'share_url': share_url,
            'token': token
        })
    
    return render(request, 'movie_app/create_movie_night.html')


def movie_night_detail(request, night_id):
    """Movie night detail view with JWT authentication"""
    token = request.GET.get('t')
    if not token:
        return render(request, 'movie_app/movie_night_auth_required.html')
    
    movie_night = verify_movie_night_token(token)
    if not movie_night:
        return render(request, 'movie_app/movie_night_invalid.html')
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return render(request, 'movie_app/movie_night_invalid.html')
    
    # Get filter parameter - default to 'now-showing' if no filter specified
    filter_type = request.GET.get('filter')
    if filter_type is None:
        filter_type = 'now-showing'  # Default when no parameter
    
    show_now_showing = filter_type == 'now-showing'
    show_already_seen = filter_type == 'already-seen'
    show_screened = filter_type == 'screened'
    show_all = filter_type == 'all'
    
    # Base queryset with annotations
    suggestions = MovieSuggestion.objects.filter(
        movie_night=movie_night
    ).select_related('movie').prefetch_related(
        'user_interactions', 'likes'
    ).annotate(
        like_count=Count('likes'),
        seen_count=Count('user_interactions', filter=Q(user_interactions__has_seen=True))
    )
    
    # Apply filter
    if show_now_showing:
        # Now Showing: not watched by group AND no one has marked as seen
        suggestions = suggestions.filter(
            is_watched_by_group=False
        ).exclude(
            user_interactions__has_seen=True
        )
    elif show_already_seen:
        # Already Seen: at least one person marked as seen
        suggestions = suggestions.filter(
            user_interactions__has_seen=True
        ).distinct()
    elif show_screened:
        # Screened: marked as watched by group
        suggestions = suggestions.filter(is_watched_by_group=True)
    # If show_all, don't apply any filter
    
    # Smart sorting: liked movies with low seen count first
    suggestions = suggestions.annotate(
        priority_score=Case(
            When(like_count__gt=0, then='like_count'),
            default=0,
            output_field=IntegerField()
        )
    ).order_by('-priority_score', 'seen_count', '-created_at')
    
    context = {
        'movie_night': movie_night,
        'suggestions': suggestions,
        'token': token,
        'filter_type': filter_type,
        'show_now_showing': show_now_showing,
        'show_already_seen': show_already_seen,
        'show_screened': show_screened,
        'show_all': show_all,
        'tmdb_api_key': getattr(settings, 'TMDB_API_KEY', ''),
    }
    
    return render(request, 'movie_app/movie_night_detail.html', context)


@require_http_methods(["GET"])
def random_movie_pick(request, night_id):
    """Get a random movie suggestion using the same filtering logic as the main view"""
    token = request.GET.get('t')
    movie_night = verify_movie_night_token(token)
    
    if not movie_night:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return JsonResponse({'error': 'Invalid movie night'}, status=400)
    
    try:
        # Get filter parameter - default to 'now-showing' if no filter specified
        filter_type = request.GET.get('filter')
        if filter_type is None:
            filter_type = 'now-showing'  # Default when no parameter
        
        # Use the EXACT same filtering logic as movie_night_detail view
        suggestions = MovieSuggestion.objects.filter(
            movie_night=movie_night
        ).select_related('movie').prefetch_related(
            'user_interactions', 'likes'
        ).annotate(
            like_count=Count('likes'),
            seen_count=Count('user_interactions', filter=Q(user_interactions__has_seen=True))
        )
        
        # Apply the same filter logic as the main view
        if filter_type == 'now-showing':
            # Now Showing: not watched by group AND no one has marked as seen
            suggestions = suggestions.filter(
                is_watched_by_group=False
            ).exclude(
                user_interactions__has_seen=True
            )
        elif filter_type == 'already-seen':
            # Already Seen: at least one person marked as seen
            suggestions = suggestions.filter(
                user_interactions__has_seen=True
            ).distinct()
        elif filter_type == 'screened':
            # Screened: marked as watched by group
            suggestions = suggestions.filter(is_watched_by_group=True)
        # If 'all', don't apply any filter
        
        # Convert to list to enable random selection
        suggestions_list = list(suggestions)
        
        if not suggestions_list:
            return JsonResponse({
                'error': 'No movies available in the current filter',
                'filter_type': filter_type
            }, status=404)
        
        # Randomly select one suggestion
        import random
        selected_suggestion = random.choice(suggestions_list)
        
        # Prepare response data
        response_data = {
            'success': True,
            'movie': {
                'id': selected_suggestion.id,
                'title': selected_suggestion.movie.title,
                'overview': selected_suggestion.movie.overview,
                'poster': selected_suggestion.movie.poster,
                'release_date': selected_suggestion.movie.release_date.isoformat(),
                'vote_average': selected_suggestion.movie.vote_average,
                'suggested_by': selected_suggestion.suggested_by,
                'created_at': selected_suggestion.created_at.isoformat(),
                'like_count': selected_suggestion.like_count,
                'seen_count': selected_suggestion.seen_count,
                'is_watched_by_group': selected_suggestion.is_watched_by_group,
                'watched_date': selected_suggestion.watched_date.isoformat() if selected_suggestion.watched_date else None,
                'genres': [genre.title for genre in selected_suggestion.movie.genre.all()],
            },
            'filter_type': filter_type,
            'total_available': len(suggestions_list)
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in random movie pick: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_movie_suggestion(request, night_id):
    """Add a movie suggestion to a movie night"""
    token = request.GET.get('t')
    movie_night = verify_movie_night_token(token)
    
    if not movie_night:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return JsonResponse({'error': 'Invalid movie night'}, status=400)
    
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        suggested_by = data.get('suggested_by', '').strip()
        
        if not movie_id or not suggested_by:
            return JsonResponse({'error': 'Movie ID and suggester name required'}, status=400)
        
        # Get or create movie
        try:
            movie = Movie.objects.get(movie_id=movie_id)
        except Movie.DoesNotExist:
            return JsonResponse({'error': 'Movie not found in database'}, status=404)
        
        # Check if already suggested
        if MovieSuggestion.objects.filter(movie_night=movie_night, movie=movie).exists():
            return JsonResponse({'error': 'Movie already suggested'}, status=400)
        
        # Create suggestion
        suggestion = MovieSuggestion.objects.create(
            movie_night=movie_night,
            movie=movie,
            suggested_by=suggested_by
        )
        
        return JsonResponse({
            'success': True,
            'suggestion_id': suggestion.id,
            'message': f'{movie.title} added successfully!'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_like(request, night_id, suggestion_id):
    """Toggle like status for a movie suggestion"""
    token = request.GET.get('t')
    movie_night = verify_movie_night_token(token)
    
    if not movie_night:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return JsonResponse({'error': 'Invalid movie night'}, status=400)
    
    try:
        data = json.loads(request.body)
        user_name = data.get('user_name', '').strip()
        
        if not user_name:
            return JsonResponse({'error': 'User name required'}, status=400)
        
        suggestion = get_object_or_404(MovieSuggestion, id=suggestion_id, movie_night=movie_night)
        
        # Get or create user interaction
        interaction, created = UserInteraction.objects.get_or_create(
            suggestion=suggestion,
            user_name=user_name,
            defaults={'has_liked': False, 'has_seen': False}
        )
        
        # Toggle like
        if interaction.has_liked:
            interaction.has_liked = False
            interaction.save()
            # Remove from likes table
            Like.objects.filter(suggestion=suggestion, user_name=user_name).delete()
            liked = False
        else:
            interaction.has_liked = True
            interaction.save()
            # Add to likes table
            Like.objects.get_or_create(suggestion=suggestion, user_name=user_name)
            liked = True
        
        return JsonResponse({
            'success': True,
            'liked': liked,
            'like_count': suggestion.get_like_count()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def toggle_seen(request, night_id, suggestion_id):
    """Toggle seen status for a movie suggestion"""
    token = request.GET.get('t')
    movie_night = verify_movie_night_token(token)
    
    if not movie_night:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return JsonResponse({'error': 'Invalid movie night'}, status=400)
    
    try:
        data = json.loads(request.body)
        user_name = data.get('user_name', '').strip()
        
        if not user_name:
            return JsonResponse({'error': 'User name required'}, status=400)
        
        suggestion = get_object_or_404(MovieSuggestion, id=suggestion_id, movie_night=movie_night)
        
        # Get or create user interaction
        interaction, created = UserInteraction.objects.get_or_create(
            suggestion=suggestion,
            user_name=user_name,
            defaults={'has_liked': False, 'has_seen': False}
        )
        
        # Toggle seen
        interaction.has_seen = not interaction.has_seen
        interaction.save()
        
        return JsonResponse({
            'success': True,
            'seen': interaction.has_seen,
            'seen_count': suggestion.get_seen_count()
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def mark_watched_by_group(request, night_id, suggestion_id):
    """Mark a movie as watched by the whole group"""
    token = request.GET.get('t')
    movie_night = verify_movie_night_token(token)
    
    if not movie_night:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return JsonResponse({'error': 'Invalid movie night'}, status=400)
    
    try:
        suggestion = get_object_or_404(MovieSuggestion, id=suggestion_id, movie_night=movie_night)
        
        suggestion.is_watched_by_group = not suggestion.is_watched_by_group
        if suggestion.is_watched_by_group:
            suggestion.watched_date = datetime.date.today()
        else:
            suggestion.watched_date = None
        suggestion.save()
        
        return JsonResponse({
            'success': True,
            'watched': suggestion.is_watched_by_group,
            'watched_date': suggestion.watched_date.isoformat() if suggestion.watched_date else None
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_suggestion(request, night_id, suggestion_id):
    """Delete a movie suggestion"""
    token = request.GET.get('t')
    movie_night = verify_movie_night_token(token)
    
    if not movie_night:
        return JsonResponse({'error': 'Invalid or expired token'}, status=401)
    
    # Verify the URL night_id matches the authenticated movie night
    if str(movie_night.id) != str(night_id):
        logger.warning(f"URL night_id {night_id} doesn't match token night_id {movie_night.id}")
        return JsonResponse({'error': 'Invalid movie night'}, status=400)
    
    try:
        suggestion = get_object_or_404(MovieSuggestion, id=suggestion_id, movie_night=movie_night)
        movie_title = suggestion.movie.title
        suggestion.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{movie_title} removed successfully'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def search_tmdb_movies(request):
    """Search TMDB API for movies"""
    query = request.GET.get('q', '').strip()
    movie_night_id = request.GET.get('movie_night_id', '').strip()
    
    if not query:
        return JsonResponse({'results': []})
    
    api_key = getattr(settings, 'TMDB_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'TMDB API key not configured'}, status=500)
    
    try:
        url = f'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': api_key,
            'query': query,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Get already suggested movie IDs for this movie night if provided
        already_suggested_ids = set()
        if movie_night_id:
            try:
                movie_night = MovieNight.objects.get(id=movie_night_id)
                already_suggested_ids = set(
                    movie_night.suggestions.values_list('movie__movie_id', flat=True)
                )
            except MovieNight.DoesNotExist:
                pass
        
        # Format results for frontend
        formatted_results = []
        for movie in data.get('results', [])[:10]:  # Limit to 10 results
            tmdb_id = movie.get('id')
            is_already_added = tmdb_id in already_suggested_ids
            
            formatted_results.append({
                'id': tmdb_id,
                'title': movie.get('title'),
                'overview': movie.get('overview', '')[:200] + ('...' if len(movie.get('overview', '')) > 200 else ''),
                'release_date': movie.get('release_date'),
                'poster_path': f"https://image.tmdb.org/t/p/w200{movie.get('poster_path')}" if movie.get('poster_path') else None,
                'vote_average': movie.get('vote_average'),
                'genre_ids': movie.get('genre_ids', []),
                'already_added': is_already_added
            })
        
        return JsonResponse({'results': formatted_results})
        
    except requests.RequestException as e:
        return JsonResponse({'error': f'TMDB API error: {str(e)}'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def add_tmdb_movie_to_db(request):
    """Add a movie from TMDB search to our database"""
    try:
        data = json.loads(request.body)
        tmdb_movie_id = data.get('tmdb_id')
        
        if not tmdb_movie_id:
            return JsonResponse({'error': 'TMDB movie ID required'}, status=400)
        
        # Check if movie already exists
        if Movie.objects.filter(movie_id=tmdb_movie_id).exists():
            return JsonResponse({'error': 'Movie already in database', 'exists': True})
        
        api_key = getattr(settings, 'TMDB_API_KEY', '')
        if not api_key:
            return JsonResponse({'error': 'TMDB API key not configured'}, status=500)
        
        # Get detailed movie info from TMDB
        url = f'https://api.themoviedb.org/3/movie/{tmdb_movie_id}'
        params = {'api_key': api_key, 'language': 'en-US'}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        movie_data = response.json()
        
        # Create movie in our database
        movie = Movie.objects.create(
            movie_id=tmdb_movie_id,
            title=movie_data.get('title', 'Unknown Title'),
            overview=movie_data.get('overview', ''),
            poster=f"https://image.tmdb.org/t/p/original{movie_data.get('poster_path')}" if movie_data.get('poster_path') else '#',
            language=movie_data.get('original_language', 'en'),
            vote_average=movie_data.get('vote_average', 0.0),
            release_date=movie_data.get('release_date') or '2000-01-01',
            popularity=movie_data.get('popularity', 0.0),
            video='#'  # We can add video fetching later if needed
        )
        
        # Add genres
        for genre_data in movie_data.get('genres', []):
            genre, created = Genre.objects.get_or_create(
                title=genre_data['name']
            )
            movie.genre.add(genre)
        
        return JsonResponse({
            'success': True,
            'movie_id': movie.movie_id,
            'title': movie.title,
            'message': f'{movie.title} added to database successfully!'
        })
        
    except requests.RequestException as e:
        return JsonResponse({'error': f'TMDB API error: {str(e)}'}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)