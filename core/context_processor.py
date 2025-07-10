from movie_app.models import Genre,Movie,Comments

# Python imports
import datetime

def processor(request):
    # Skip context processing for Inertia.js requests
    if hasattr(request, 'META') and request.META.get('HTTP_X_INERTIA'):
        return {}
    
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    all_categories = Genre.objects.filter(is_active=True)
    latest_movies_processor = Movie.objects.order_by('-release_date').filter(is_active=True)[:50]
    latest_comments = Comments.objects.all()[:10]
    return {'categories':all_categories, 'latest_movies_processor':latest_movies_processor, 'latest_comments':latest_comments}